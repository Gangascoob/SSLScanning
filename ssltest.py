import subprocess
import os
import time
import json
import datetime

OUTPUT_FOLDER = "Outputs"

def get_final_results_file():
    today_date = datetime.date.today().strftime("%Y-%m-%d")
    final_results_file = f"outputs_{today_date}.txt"
    return final_results_file


def call_api_and_save_response(api_url, email_header, output_file, write):
    try:
        # Construct the curl command as a list of arguments
        
        curl_command = f"curl --location '{api_url}' --header '{email_header}'"
        
        process = subprocess.Popen(curl_command, shell=True, stdout=subprocess.PIPE)
        output, _= process.communicate()
        
        
        output_file_path = os.path.join(OUTPUT_FOLDER, output_file)
        
        with open(output_file, 'w') as file:
                file.write(output.decode('utf-8'))
                print(f"API response saved to {output_file}")
                
    except Exception as e:
        print(f"Error occurred: {e}")
        
        
def parse_api_response(output_file_path, api_url):
    try:
         while True:
            final_results_file = get_final_results_file()
         
            with open(output_file_path, 'r') as file:
                data = json.load(file)
            status = data.get('status')
            print(f"Status: {status}")
            
            if status == 'ERROR':
                statusMessage = data.get('statusMessage')
                print(f"Status Message: {statusMessage}")
                with open(final_results_file, 'a') as final_file:
                    final_file.write(f"{api_url}: {statusMessage}\n")
                break
            
            
            elif status == 'READY':
                status_info = data['endpoints'][0]['statusMessage']
                if status_info == 'Ready':
                    grade_info = data['endpoints'][0]['grade']
                    print(f"Grade: {grade_info}")
                    with open(final_results_file, 'a') as final_file:
                        final_file.write(f"{api_url}: {grade_info}\n")
                else:
                    print(f"No Grade Found - Status Message is: {status_info}")
                    with open(final_results_file, 'a') as final_file:
                        final_file.write(f"{api_url}: {status_info}\n")
                break
                
            else:
                print(f"Status is {status}. Waiting for 60 seconds and checking again.")
                time.sleep(60)
                call_api_and_save_response(api_url, email_header, output_file_path, True)
                parse_api_response(output_file_path, api_url)
                
            #else:
            #    print("Invalid status:", status)
            #    break
        
    except Exception as e:
        print(f"Error parsing API response: {e}")
        return None
        

def process_api_url(api_url, email_header):
    try:
        output_file = f"{api_url.replace('/', '_').replace(':', '_')}_output.txt"
        output_file_path = os.path.join(OUTPUT_FOLDER, output_file)
        call_api_and_save_response(api_url, email_header, output_file_path, True)
        parse_api_response(output_file_path, api_url)
    except Exception as e:
        print(f"Error processing API URL {api_url}: {e}") 
        

        
        
def process_api_urls(api_urls_file, email_header):
    try:
        with open(api_urls_file, 'r') as file:
            api_urls = file.readlines()
            
        for api_url in api_urls:
            api_url = api_url.strip()
            process_api_url(api_url, email_header)
            
        remove_duplicates_from_file()
    except Exception as e:
            print(f"Error processing API URLs: {e}")


def remove_duplicates_from_file():
    try:
        final_results_file = get_final_results_file()
        lines_seen = set()
        output_lines = []
        
        with open(final_results_file, 'r') as file:
            for line in file:
                if line.strip() not in lines_seen:
                    output_lines.append(line)
                    lines_seen.add(line.strip())
                    
        with open(final_results_file, 'w') as file:
            file.writelines(output_lines)
            
    except Exception as e:
        print(f"Error removing duplicates from file: {e}")

        
# Example usage:
api_url = "https://api.ssllabs.com/api/v4/analyze?host=safe.epcc.ed.ac.uk"
email_header = "email: g.scobie@epcc.ed.ac.uk"
output_file = "./output.txt"
api_urls_file = "./domainnames.txt"
#final_results_file = "./final.txt"



process_api_urls(api_urls_file, email_header)

