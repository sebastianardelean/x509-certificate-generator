# Instructions for generating X.509 certificates using QKD keys

## Environment setup

1. Install Python 3
2. Clone the [repository](https://github.com/sebastianardelean/x509-certificate-generator) 
3. Install Python dependencies: `pip install -r requirements.txt`
4. Run the script using the following command:

```python
python generate_x509_certificate.py --key <QKD key in Base64> \
    --days [certificate validity in days] \
    --prefix [output file prefix] \
    --C [country name] \
    --ST [state/province name] 
    --L [locality name]
    --O [organization name]
    --OU [organizational unit name]
    --CN [common name]
```
The arguments between `<>` are mandatory while the others--those between `[]`--are optional.

Example:

```python
python generate_x509_certificate.py --key NiXDkmgcAztCFzyhO8XI+COj1Y1pEMDR8H0LzxZxoFo= \
    --prefix upt_cert \
    --C RO \
    --ST Timis \
    --L Timisoara \ 
    --O "Politehnica University Timisoara" \ 
    --OU "UPT RONAQCI" \
    --CN "UPT RONAQCI" \
```
