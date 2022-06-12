# LTP-API client lib
Library for client calls to LTP-API.

## Installing

* Install ```requests``` system packages
* Build & Install ltp-api-client-lib with poetry:
```python
pip install poetry
git clone https://github.com/CESNET/ltp-api-client-lib
cd ltp-api-client-lib
poetry build
cd dist
tar -xvf ltp-api-client-lib-0.1.0.tar.gz
pip install -e ltp-api-client-lib-0.1.0/
```

## How to use CLI
### 1) You need token 
#### How to get token

1) Login to api web (`https://url:<port>/api/`)  or ltp web (`https://url:<port>`).
2) After all of this you can create token on `https://url:<port>/api/`
    in `/auth/token/create/` endpoint. This token may expire so this step you may repeated after while.
    this will return something like this:
    ```
        {
          "expiry": "2020-04-23T05:05:13.639245",
          "token": "5616b341f38d64d13a33c487bb852e1f12b5d0a3390433c56c13a0790b6f694c", <-- THIS IS TOKEN
          "user": {
            "username": "username for your admin"
          }
        }
    ```
Now you can call endpoint with token.

For CESNET LTP you have to generate the token in the [LTP GUI](https://du.cesnet.cz/cs/navody/ltp/start#user_profile).

### 2) You need to know uuid group 

Then you have all information what you need to use CLI.

In case of CESNET LTP group identificator can be found in the [user profile](https://du.cesnet.cz/cs/navody/ltp/start#user_profile).

## Examples
### Help
```
❯ python3 ltp_api_client.py --help
Usage: ltp_api_client.py [OPTIONS] COMMAND [ARGS]...

Options:
  -t, --token TEXT    Token for communication with LTP API  [required]  
  -c, --context TEXT  Context/group for communication with LTP API  [required] 
  -a, --address TEXT  Http address of  LTP API
  --help              Show this message and exit.

Commands:
  archive
  audit
  bagit
```

Upload/Create:
```
python3 ltp_api_client.py -t $API_KEY -c 50b6eGroup_ID409917 -a https://ltp.cesnet.cz/api/ archive create -d '{"name":"test python cli", "user_metadata":{}}' -p /home/user/Desktop/my_bagit_arch.zip 
```
Download:
```
python3 ltp_api_client.py -t $API_KEY -c 50b6eGroup_ID409917 -a https://ltp.cesnet.cz/api/ archive download -i 163 -p /tmp/testout.zip
```
List:
```
python3 ltp_api_client.py -t $API_KEY -c 50b6eGroup_ID409917 -a https://ltp.cesnet.cz/api/ archive list
```
Update metadata:
```
python3 ltp_api_client.py -t $API_KEY -c 50b6eGroup_ID409917 -a https://ltp.cesnet.cz/api/ archive update -d '{"name":"test python cli", "user_metadata":{"author":"Albert"}}' -i 166
```
List audit logs:
```
python3 ltp_api_client.py -t $API_KEY -c 50b6eGroup_ID409917 -a https://ltp.cesnet.cz/api/ audit list
```
Create bagit:
```
python3 ltp_api_client.py bagit build -p <path> -j "{'Contact-Name': 'John Kunze'}"
```
Validate bagit:
```
python3 ltp_api_client.py bagit validate -p <path>
```
Zip dir:
```
python3 ltp_api_client.py bagit zipit -z <zip_name> -p <path>
```