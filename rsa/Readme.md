# Generate X.509 certificates using RSA algorithm

## Environment setup

1. Install Python 3
2. Clone the [repository](https://github.com/sebastianardelean/x509-certificate-generator) 
3. Install Python dependencies: `pip install -r requirements.txt`
4. Install rng-tools. On Debian based OS the command is `sudo apt install rng-tools`. The package can be also built from [source code](https://github.com/nhorman/rng-tools)
5. Run the Python script using the command

```
python get_bytes.py --cert certificate.pem --key key.pem --password password --url url_enc_keys --output output.bin --count 50

```
The password is optional and it shall be used only if the key is encrypted with password!

Example:

```
python get_bytes.py --cert certificate.pem --key ronaqci-key.pem --password uptpassword --url https://172.24.162.133/api/v1/keys/CONS_TIM_UVT/enc_keys --output bytestream.bin --count 50
```

6. Feed the entropy using [rngd](https://wiki.networksecuritytoolkit.org/nstwiki/index.php?title=HowTo_Fix_The_rngd.service) by running the command: `sudo /sbin/rngd --rng-device output.bin`. 
7. Create X.509 certificate: `openssl req -x509 -sha256 -nodes -newkey rsa:4096 -keyout outkey.key -days 365 -out certificate.pem`

