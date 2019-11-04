import requests

def check_hash(hash):
    """Check the hash to the endpoint were the api Docker has been deployed
    
    Args:
        hash (str): Hash string obtained with airdrop_leak script
    
    Returns:
        str: Phone received or "None"
    """

    url = ""
    querystring = {"hash": hash}
    headers = {
        '',
    }
    response = requests.request("GET", url, headers=headers, params=querystring)
    if response.status_code == 200:
        return response.json().get("phone", "None")
    return "None"

