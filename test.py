import jwt

token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiZGM1Y2I2NWItOGM2Ny00MTZjLWFmODItZmFhM2NlYjg4OTJjIiwiZXhwIjoxNzM3ODUwMTk3fQ.1seo4MWtGgoRTju5JS3KhVrka-4p0Yu1f_Phi2kmCtI"
decoded = jwt.decode(token, "0067b9d7ceb4a5796720198078a9f4e30494f3f37047b18c4c9ba722f4ebc0bc", algorithms=["HS256"])
print(decoded)