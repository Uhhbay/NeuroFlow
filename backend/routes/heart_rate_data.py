import json
import cv2
import numpy as np
from scipy.signal import butter, convolve, find_peaks, filtfilt
from fastapi import FastAPI, Query
import neurokit2 as nk  # Import NeuroKit2 for stress score calculation

app = FastAPI()


class NumpyEncoder(json.JSONEncoder):
    """Special JSON encoder for numpy types."""

    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        return super().default(obj)


def butter_highpass(cutoff, fs, order=5):
    nyq = 0.5 * fs
    normal_cutoff = cutoff / nyq
    b, a = butter(order, normal_cutoff, btype="high", analog=False)
    return b, a


def butter_lowpass(cutoff, fs, order=5):
    nyq = 0.5 * fs
    normal_cutoff = cutoff / nyq
    b, a = butter(order, normal_cutoff, btype="low", analog=False)
    return b, a


def filter_all(data, fs, order=5, cutoff_high=8, cutoff_low=25):
    b, a = butter_highpass(cutoff_high, fs, order=order)
    highpassed_signal = filtfilt(b, a, data)
    d, c = butter_lowpass(cutoff_low, fs, order=order)
    bandpassed_signal = filtfilt(d, c, highpassed_signal)
    return bandpassed_signal


def process_signal(y, order_of_bandpass, high, low, sampling_rate, average_filter_sample_length):
    filtered_signal = filter_all(y, sampling_rate, order_of_bandpass, high, low)
    squared_signal = filtered_signal ** 2
    b = (np.ones(average_filter_sample_length)) / average_filter_sample_length
    a = np.ones(1)
    averaged_signal = convolve(squared_signal, b)
    averaged_signal = filtfilt(b, a, squared_signal)
    return averaged_signal


def calculate_hrv(rr_intervals):
    """Calculate HRV metrics: SDNN, RMSSD, and pNN50."""
    rr_intervals_ms = np.array(rr_intervals) * 1000  # Convert to milliseconds
    sdnn = np.std(rr_intervals_ms)  # Standard deviation of RR intervals
    rmssd = np.sqrt(np.mean(np.diff(rr_intervals_ms) ** 2))  # Root mean square of successive differences
    nn50 = sum(np.abs(np.diff(rr_intervals_ms)) > 50)  # Count of differences > 50ms
    pnn50 = (nn50 / len(rr_intervals_ms)) * 100  # Percentage of NN50 intervals
    return {"SDNN": sdnn, "RMSSD": rmssd, "pNN50": pnn50}


def calculate_stress_score(peak_indices, sampling_rate):
    """Calculate a stress score using NeuroKit2."""
    # Convert peak indices to a binary array (required by NeuroKit2)
    binary_peaks = np.zeros(peak_indices[-1] + 1)  # Create an array the size of the signal
    binary_peaks[peak_indices] = 1  # Set peaks as 1

    # Compute HRV metrics
    hrv_metrics = nk.hrv(binary_peaks, sampling_rate=sampling_rate, show=False)
    stress_index = hrv_metrics.get("HRV_SI", None)  # Stress Index (HRV_SI)
    return stress_index


def give_bpm_and_hrv(averaged, time_bw_fram):
    r_min_peak = min(averaged) + (max(averaged) - min(averaged)) / 16
    r_peaks = find_peaks(averaged, height=r_min_peak)
    total_peaks = len(r_peaks[0])

    if total_peaks <= 1:  # Not enough peaks to calculate BPM
        print("Insufficient peaks detected for BPM and HRV calculation.")
        return {"BPM": 0, "HRV": {"SDNN": 0, "RMSSD": 0, "pNN50": 0}, "Stress_Score": None}

    # Convert peak indices to RR intervals
    rr_intervals = [
        (r_peaks[0][i + 1] - r_peaks[0][i]) * time_bw_fram
        for i in range(total_peaks - 1)
    ]

    avg_time_bw_peaks = np.mean(rr_intervals)
    bpm = float(60.0 / avg_time_bw_peaks)

    # Calculate HRV metrics
    hrv_metrics = calculate_hrv(rr_intervals)

    # Calculate Stress Score using NeuroKit2
    stress_score = calculate_stress_score(r_peaks[0], sampling_rate=int(1 / time_bw_fram))

    return {
        "BPM": bpm,
        "HRV": hrv_metrics,
        "Stress_Score": stress_score
    }


@app.get("/api")
async def get_beats_per_min(query: str = Query(...)):
    # Validate video file
    if not cv2.VideoCapture(query).isOpened():
        return {"error": "Video file could not be opened. Please check the path."}

    video_data = cv2.VideoCapture(query)
    fps = video_data.get(cv2.CAP_PROP_FPS)
    frame_count = int(video_data.get(cv2.CAP_PROP_FRAME_COUNT))

    if frame_count == 0:
        return {"error": "Video contains no frames."}

    time_bw_frame = 1.0 / fps
    R, G, B = np.array([]), np.array([]), np.array([])

    while True:
        ret, frame = video_data.read()
        if not ret:
            break

        no_of_pixels = 0
        sumr, sumg, sumb = 0.0, 0.0, 0.0  # Initialize as floats

        for i in frame[int((len(frame) - 100) / 2): int((len(frame) + 100) / 2)]:
            for j in i[int((len(frame[0]) - 100) / 2): int((len(frame[0]) + 100) / 2)]:
                sumr += float(j[2])  # Cast to float
                sumg += float(j[1])
                sumb += float(j[0])
                no_of_pixels += 1

        R = np.append(R, sumr / no_of_pixels)
        G = np.append(G, sumg / no_of_pixels)
        B = np.append(B, sumb / no_of_pixels)

    R, G, B = R[100:-100], G[100:-100], B[100:-100]

    r_cutoff_high, r_cutoff_low, r_order_of_bandpass = 10, 100, 5
    r_sampling_rate = 8 * int(fps + 1)
    r_average_filter_sample_length = 7

    r_averaged = process_signal(R, r_order_of_bandpass, r_cutoff_high, r_cutoff_low, r_sampling_rate, r_average_filter_sample_length)

    # Calculate BPM, HRV, and Stress Score
    bpm_and_hrv = give_bpm_and_hrv(r_averaged, time_bw_frame)

    result = {
        "r_avg": r_averaged.tolist(),
        "BPM": bpm_and_hrv["BPM"],
        "HRV": bpm_and_hrv["HRV"],
        "Stress_Score": bpm_and_hrv["Stress_Score"],
    }

    return result


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)
