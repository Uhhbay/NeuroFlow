## Inspiration
We realized that there weren't any good metrics out there for measuring stress, especially on healthcare wearables. Stress was primarily rated on subjective scales, but we wanted to bring a more scientific approach. We envisioned a world in which someone's "stress score" could be reported along with tests like an HA1C.

## What it does
Utilizes a novel, scalable means of gathering biological data Correlates that biological data to a quantitative metric for stress, derived from Heart Rate Variation (HRV) Enables early detection of stress-related disorders, decreasing healthcare costs Enhances the suite of data available to healthcare providers

## How we built it
For this project, we utilized a FARM stack, calling APIs related to processing PPG data. We used video analysis of a person's finger pressed against their camera with the flash on for 15 seconds in order to get PPG Data. As blood flows changes modulate light absorption, each video frame is taken and the average red channel intensity from from the center of the frame is extracted. The red channel signal is then processed using a bandpass filter to isolate heartbeat related frequencies. Peaks in the filtered signal is taken to represent blood volume pulses and the intervals between detected peaks (RR intervals) is used to calculate bpm, SDNN, RMSSD, and pNN50, which is compared to national averages in order to produce a "stress score".

## Challenges we ran into
One particular challenge we ran into was making the project more patient-focused rather than provider focused. Initial drafts of the project worked on the PPG data to predict wakefulness, which was useful for providers but not necessarily for patients. We figured out that the PPG data could also be used to predict stress levels -- and from there, it was quite the effort to change the scope of the project 12 hours in.

## Accomplishments that we're proud of
Finishing the project on time was first and foremost, the most outstanding challenge. We were able to use a cutting-edge technology to make healthcare more accessible to virtually anyone with a phone.

## What we learned
We learned to be flexible -- whether it was with the scope of the project, with the technologies we were willing to use/not use, and with how we were marketing our project. We were constantly reevaluating what the best way to do something was, what to prioritize, and what to refine.

## What's next for NeuroFlow
We envision NeuroFlow increasing the availability of mental health data, driving both its acceptance and its awareness. In addition, the focus will be on availability and access, especially to impacted populations. Our primary motivator for this project was making healthcare data accessible with something everyone has - a phone. We anticipate continuing this, looking for other data suites that can be encompassed by everyday technology. It's our goal to make this type of data collection both accessible and passive -- something that is so low-friction you don't even notice it's there.

### Devpost Link ### 
https://devpost.com/software/neuroflow?ref_content=my-projects-tab&ref_feature=my_projects
