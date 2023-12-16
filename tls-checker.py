import ssl
import socket
import sys
import csv
import json
import concurrent.futures
import random
import os
import re
import zipfile
try:
    import dns.resolver
    import requests
    from progress.spinner import MoonSpinner
except ImportError:
    print('\nX Please install required modules X'
          '\n• Commands for manually installing the requirements:\n'
          '\n> pip install -r requirements.txt\n'
          '\nor\n'
          '\n> pip3 install -r requirements.txt\n'
         )
    install = input('- Would you like to install requirements automatically? [y=YES, n=NO]:').strip().lower()
    if install == 'y':
        import subprocess
        try:
            subprocess.run('pip install -r requirements.txt'.split(' '))
        except FileNotFoundError:
            subprocess.run('pip3 install -r requirements.txt'.split(' '))
        import dns.resolver
        import requests
        from progress.spinner import MoonSpinner
    elif install == 'n':
        sys.exit(0)
    else:
        sys.exit(1)


def get_info(web_addrs: list) -> dict:
    api_token = '3bd22fe89c5c42d386d84297d53389d3'
    port = 443
    context = ssl.create_default_context()
    context.set_alpn_protocols(['h2', 'http/1.1', 'h3'])
    result = {}
    spinner = MoonSpinner('••••••••••••••••••••••••••••••••••••• ')
    for web_addr in web_addrs:
        spinner.next()
        try:
            sock = socket.create_connection((web_addr[0], port), timeout=5)
            conn = context.wrap_socket(sock, server_hostname=web_addr[0])
            resolve_server = dns.resolver.resolve(web_addr[0])
            ip_server = [rdata for rdata in resolve_server]
            url = f'https://api.findip.net/{ip_server[0]}/?token={api_token}'
            response = requests.get(url, timeout=5).json()
            cipher = conn.cipher()
            alpn = conn.selected_alpn_protocol()
            iso_code = response['country']['iso_code']
            AS_organization = response['traits']['autonomous_system_organization']
            country = response['country']['names']['en']
            city = response['city']['names']['en']
            issuer = conn.getpeercert()['issuer'][1][0][1]
            subject_alt_name = [dns[1] for dns in conn.getpeercert()['subjectAltName']]
            random.shuffle(subject_alt_name)
            subject_alt_name_chunk = subject_alt_name[0: 5] if len(subject_alt_name) > 5 else subject_alt_name
        except:
            continue
        else:
            if get_iso_name and get_AS_organization_name:
                condition = (cipher[1] == 'TLSv1.3') \
                and ((alpn == 'h2') or (alpn == 'h3')) \
                and (get_iso_name == iso_code) \
                and(pattern.findall(AS_organization))
            elif get_iso_name:
                condition = (cipher[1] == 'TLSv1.3') \
                and ((alpn == 'h2') or (alpn == 'h3')) \
                and (get_iso_name == iso_code)
            elif get_AS_organization_name:
                condition = (cipher[1] == 'TLSv1.3') \
                and ((alpn == 'h2') or (alpn == 'h3')) \
                and (pattern.findall(AS_organization))
            else:
                condition = (cipher[1] == 'TLSv1.3') \
                and ((alpn == 'h2') or (alpn == 'h3'))
            if condition:
                print(
                      f'\naddress = {web_addr[0]}\nalpn = {conn.selected_alpn_protocol()}'
                      f'\nissuer = {issuer}\ncipher = {cipher[0]}\nTLS = {cipher[1]}'
                      f'\nkey_length = {cipher[2]}\ncountry = {country}'
                      f'\niso_code = {iso_code}\ncity = {city}'
                      f'\nAS organization = {AS_organization}'
                      f'\nsubject_alt_name = {" | ".join(map(str, subject_alt_name_chunk))}\n',
                      end=''
                     )
                result[web_addr[0]] = [
                                    issuer, alpn, cipher[0], cipher[1], 
                                    cipher[2], country, iso_code, city,
                                    AS_organization, subject_alt_name
                                   ]
            else:
                continue
    return result


def main() -> None:
    outlist = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=30) as executer:
        tasks = [executer.submit(get_info, url_group) for url_group in input_urls]
        for task in concurrent.futures.as_completed(tasks):
            result = task.result()
            if result:
                outlist.append(result)
    
    save_output(outlist)
    outq = input('\n- Do you need sorted output? [y=YES, n=NO]:').strip().lower()
    if outq == 'y':
        print('+ The output was saved in sorted.txt file.')
        sort_output(outlist)
    elif outq == 'n':
        sys.exit(0)
    else:
        sys.exit(1)

def sort_output(lst: list) -> None:
    output_urls = [item for sublst in lst for item in sublst]
    not_sorted_dict = {}
    sorted_lst = []

    for url in output_urls:
        not_sorted_dict[web_addrs_dict[url]] = url
    sorted_lst = sorted(not_sorted_dict.items())

    print(f'\nrank\t\turl\n{"-"*24}')
    for item in sorted_lst:
            print(f'{item[0]}\t\t{item[1]}')
    
    sorted_file = os.path.join(base_path, 'sorted.txt')
    with open(sorted_file, 'w', encoding='utf-8') as f:
        f.write(f'rank\t\turl\n{"-"*24}\n')
        for item in sorted_lst:
            f.write(f'{item[0]}\t\t{item[1]}\n')
    
def save_output(lst: list) -> None:
    result_file = os.path.join(base_path, 'result.json')
    with open(result_file, 'w', encoding='utf-8') as f:
        json.dump(lst, f, ensure_ascii=False, indent=4)


if __name__ == '__main__':
    # initialize the search process
    print('''
88888888888888     d8b        d8b               d8888888b    888 .d88888b. 888b     d888 
    888    888     Y8P        Y8P              d888888888b   888d88P" "Y88b8888b   d8888 
    888    888                                d88P88888888b  888888     88888888b.d88888 
    888    88888b. 888.d8888b 888.d8888b     d88P 888888Y88b 888888     888888Y88888P888 
    888    888 "88b88888K     88888K        d88P  888888 Y88b888888     888888 Y888P 888 
    888    888  888888"Y8888b.888"Y8888b.  d88P   888888  Y88888888     888888  Y8P  888 
    888    888  888888     X88888     X88 d8888888888888   Y8888Y88b. .d88P888   "   888 
    888    888  888888 88888P'888 88888P'd88P     888888    Y888 "Y88888P" 888       888
         ''')
    print('• https://github.com/ImanMontajabi/TLS-Checker')
    print('• version: 1.2.4')
    print('\n[ You can ignore the questions and just press Enter ↩ ]\n')
    # base path of files for read and save them
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    get_file_name = input('- Which file? [i=irani.csv or 1=file1.csv or 2=file2.csv]:').strip().lower()
    if get_file_name == 'i':
        file_name = 'irani'
        print('+ irani.csv is selected.')
    elif get_file_name == '1':
        file_name = 'file1'
        print('+ file1.csv is selected.')
    else:
        file_name = 'file2'
        print('+ file2.csv is selected.')

    # this list includes all urls from csv
    web_addrs = []
    addr_file = os.path.join(base_path, f'{file_name}.csv')
    try:
        with open(addr_file) as urls:
            csv_reader = csv.reader(urls)
            for rank, row in enumerate(csv_reader):
                web_addrs.append([row[0], rank + 1])
                
                
    except FileNotFoundError:
        zip_file = os.path.join(base_path, 'csvfiles.zip')
        zip_file_out = os.path.join(base_path, '')
        with zipfile.ZipFile(zip_file, 'r') as zip_ref:
            zip_ref.extractall(zip_file_out)
        os.remove(zip_file)

        with open(addr_file) as urls:
            csv_reader = csv.reader(urls)
            for rank, row in enumerate(csv_reader):
                web_addrs.append([row[0], rank + 1])
                

    len_webaddr = len(web_addrs)
    """ 
    Get length of csv chunk and
    fill input_urls list for threads
    """
    try:
        how_many = int(input(f'- How many url of "{file_name}.csv" do you want to check? [1-{len_webaddr}]:').strip())
        print(f'+ {how_many} urls are selected.')
    except ValueError:
        how_many = len_webaddr
        print(f'+ {how_many} urls are selected.')

    how_many = max(how_many, 1)
    how_many = min(how_many, len_webaddr)

    randomized = input('- Do you want to use randomized search? [y=YES, n=NO]:').strip().lower()
    if randomized == 'y':
        random.shuffle(web_addrs)
        print('+ Randomized search is selected.')
    elif randomized == 'n':
        print('+ Normal search is selected.')
    else:
        random.shuffle(web_addrs)
        print('+ Randomized search is selected.')

    input_urls = []
    # make input of threads
    length = 30 if how_many >= 30 else 1
    for i in range(0, how_many, length):
        input_urls.append(web_addrs[i:min(i+length, how_many)])
    # make a dictionary to find rank and url in next steps
    web_addrs_dict = dict(web_addrs)    
    # set iso code
    print('! Guide: https://en.wikipedia.org/wiki/List_of_ISO_3166_country_codes')
    get_iso_name = input('- preferred country? [DE=Germany, NL=Netherland,...]:').strip().upper()

    # set AS organization name and regex for filter AS organization names during search
    get_AS_organization_name = input('- preferred AS Organization? [Hetzner, Vultr, OVH, Akamai,...]:').strip().lower()
    pattern = re.compile(r'[^.,\s]*'+get_AS_organization_name+'[^.,\s]*[.,]?', re.IGNORECASE)
    #start main process
    main()
    

    
