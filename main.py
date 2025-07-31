import json, requests, traceback, random, string, threading, sys, ctypes
from sys import *
from bs4 import BeautifulSoup as soup
from discord_webhook import DiscordEmbed, DiscordWebhook
from time import sleep
from datetime import datetime
from colorama import init
from classes.logger import logger
log = logger().log

ctypes.windll.kernel32.SetConsoleTitleW('Supply Store Image Monitor')

try:
    groups = json.loads(open('branding.json').read())['groups']
except:
    log('Failed to load branding. Exiting...')
    sleep(2)
    sys.exit()



#{'SKU':'', 'title':''}

sku = [{'SKU':'DH2684-001', 'title':'NIKE X SACAI X FRAGMENT LD WAFFLE - LIGHT SMOKE GREY/WHITE-BLACK'}, {'SKU':'DH2684-400', 'title':'NIKE X SACAI X FRAGMENT LD WAFFLE - BLUE VOID/WHITE-OBSIDIAN'}]

log('Loaded {} skus for monitoring'.format(str(len(sku))))


directory = 'proxies.txt'
usingProxies = False
proxies = []

try:
    with open(directory) as k:
        initProxies = k.read().splitlines()

    try:
        for proxy in initProxies:
            proxy = proxy.split(':')
            ip = proxy [0]
            port = proxy[1]
            try:
                user = proxy[2]
                password = proxy[3]
                finProxy = {'http':'http://'+user+':'+password+'@'+ip+':'+port, 'https':'http://'+user+':'+password+'@'+ip+':'+port}
            except:
                finProxy = {'http':'http://'+ip+':'+port, 'https':'http://'+ip+':'+port}
            proxies.append(finProxy)
    except Exception as e:
        pass
except Exception as e:
    log('Error: '+str(e))

if len(proxies) != 0:
    log('Successfully loaded '+str(len(proxies))+' proxies from '+str(directory))
    usingProxies = True
else:
    log('Loaded 0 proxies. Running localhost')

        
def main():
    def monitor(x):
        first_run = 0

        loadedSkus = []
        headers = {'Cache-Control':'no-store, max-age=0', 'Strict-Transport-Security': 'max-age=0'}
        delay = 3
        slug = '['+sku[x]['title']+' - '+sku[x]['SKU']+'] : '
        while True:
            try:
                log(slug+'Checking for image load...')
                link = 'https://www.supplystore.com.au/images/items/{}/{}/1.jpg'.format(sku[x]['SKU'], sku[x]['SKU'])
                try:
                    if usingProxies:
                        e2 = requests.get(link, headers = headers, proxies=random.choice(proxies), timeout=5)
                    else:
                        e2 = requests.get(link, headers = headers, timeout=5)
                except:
                    log(slug+'Failed to connect to supply store')
                    sleep(delay)
                    continue

                if e2.status_code== 404:
                    log(slug+'Image not loaded [Status Code: 404]')
                    log(slug+'Delaying {}s till next run'.format(str(delay)))
                    if sku[x]['SKU'] in loadedSkus: 
                        loadedSkus.remove(sku[x]['SKU'])
                    sleep(delay)
                else:
                    if e2.status_code == 200:
                        if first_run == 0:
                            loadedSkus.append(sku[x]['SKU'])
                            log(slug+'First run and product is loaded. Skipping')
                            sleep(delay)
                            first_run = first_run + 1
                        elif sku[x]['SKU'] not in loadedSkus:    
                            log(slug+'Image is now loaded. Sending webhook')
                            for u in groups:                
                                try:
                                    webhook = DiscordWebhook(url=groups[u]['webhook'], username = 'Supply Store Backend', avatar_url=groups[u]['image'])
                                    embed = DiscordEmbed(title = sku[x]['title'],description='Product is likely to drop within the hour. Please login!', color=groups[u]['colour'])
                                    embed.url = 'https://www.supplystore.com.au/shop/search.aspx?q='+sku[x]['SKU']
                                    embed.add_embed_field(name = 'SKU', value = sku[x]['SKU'], inline = True)
                                    embed.set_thumbnail(url=link)
                                    embed.set_author(name='New Backend Load')
                                    embed.set_footer(text=groups[u]['footer'],icon_url =groups[u]['image'])
                                    embed.set_timestamp()
                                    embed.add_embed_field(name = "Useful Links", value = '[Clear Cart](https://www.supplystore.com.au/shop/checkout/cart.aspx?quantityInput_0=0)\n[Login](https://www.supplystore.com.au/shop/login.aspx)\n[Checkout](https://www.supplystore.com.au/shop/checkout/address.aspx)', inline = False)
                                    webhook.add_embed(embed)
                                    webhook.execute()
                                    log(slug+'Sent webhook for {} for {}'.format(sku[x]['title'], u))
                                except Exception as e:
                                    log(slug+'Failed to send webhook for {} for {}'.format(sku[x]['title'], u))
                                    log(slug+'Error: {}'.format(str(e)))    
                                                                                        #log('Traceback: {}'.format(traceback.format_exc())) 
                            loadedSkus.append(sku[x]['SKU'])
                        else:
                            log(slug+'Product already loaded. Skipping'), sleep(delay)    
                    else:
                        log(slug+'Failed to request link [Status Code:{}]'.format(str(e2.status_code)))                      

            except Exception as e:
                                log(slug+'Something went wrong with the monitor. Restarting', "error")
                                log(slug+'Error: {}'.format(str(e)))
                                sleep(int(delay))

            first_run = first_run + 1
            

    for x in range(len(sku)):
            slug = '['+sku[x]['title']+' - '+sku[x]['SKU']+'] : '
            try:
                log(slug+'Starting monitor...')
                (threading.Thread(target=monitor, args=(x, ))).start()
            except Exception as e:
                log(slug+'EXCEPTION OCCURED: '+str(e))
                log(slug+'STOPPING TASK...'), sys.exit()

    
log('Supply Store Backend monitor')
main()
