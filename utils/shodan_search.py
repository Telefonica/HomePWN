import shodan
from utils.custom_print import print_info, print_error, print_ok

def get_shodan_search_matches(apikey, to_search):
    try:
        shodan_api = shodan.Shodan(apikey)
        print_info(f"Making request to Shodan. Search: {to_search}")
        result = shodan_api.search(to_search)
        return result["matches"]
    except Exception as e:
        print_error(e)
        return None


def shodan_search(file_to_save, apikey, to_search):
    data = get_shodan_search_matches(apikey, to_search)
    if data:
        print_ok("Data collected!")
        for entry in data:
            host = entry['ip_str']
            city = entry['location']['city']
            country = entry['location']['country_name']
            if city:
                country = city + f"({country})"
            port = entry['port']
            data =  f"{host}:{port}"
            file_to_save.write(f"{data.ljust(20)} - {country}\n")
        return True
    else:
        print_info("No data recollected")
        return False
        