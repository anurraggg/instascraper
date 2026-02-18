import pandas as pd
import os
import shutil

# New URLs
urls = """
https://www.instagram.com/reel/DJoetASTxYo/?igsh=enNxeDUxOGwzNzBy
https://www.instagram.com/reel/DJ_mxM0pEot/
https://www.instagram.com/p/DJ1r_Q2TpWv/
https://www.instagram.com/reel/DJ1nNu6ReYp/
https://www.instagram.com/reel/DJwWxxdI-uA/
https://www.instagram.com/reel/DJofDxjyZKX/
https://www.instagram.com/p/DKWm0CLyY1L
https://www.instagram.com/p/DKTqKbuzUvd
https://www.instagram.com/p/DKUCUCmoese
https://www.instagram.com/p/DKUPK8jz_iL
https://www.instagram.com/p/DKUWF3KtOAB
https://www.instagram.com/reel/DJssDgXywPY/
https://www.instagram.com/reel/DJHKOJ1vWzS/
https://www.instagram.com/reel/DJO2ZJ4PXpV/
https://www.instagram.com/reel/DJYOtuwS2PG/
https://www.instagram.com/reel/DJHEBqCBdCQ/
https://www.instagram.com/reel/DJYs24HyBug/
https://www.instagram.com/reel/DJLSsgtyFSi/
https://www.instagram.com/reel/DJGoEx5vxM2/
https://www.instagram.com/reel/DKZhZPAymNR/
https://www.instagram.com/reel/DJJ_flGvYvA/
https://www.instagram.com/reel/DJLc6Xhpmi5/
https://www.instagram.com/reel/DJEvsXQpDYl/
https://www.instagram.com/reel/DJGm4waBghs/
https://www.instagram.com/reel/DJGqQBGzTQZ/
https://www.instagram.com/reel/DIQVWuAxhKL/
https://www.instagram.com/reel/DINo6hfSKf5/
https://www.instagram.com/reel/DITVz4Epayu/
https://www.instagram.com/reel/DITgCQVzmF9/
https://www.instagram.com/reel/DMFsM-6T4dd/?igsh=MW1ubDZlc2p2cWZ3bQ==
https://www.instagram.com/reel/DMNE0bby-PO/?igsh=OWZzc3l3ajgyY3li
https://www.instagram.com/reel/DMAgp4NRor4/?igsh=MWY0MDdsZjMwbHQ4bQ==
https://www.instagram.com/reel/DHbHMntobRm/?igsh=NTc4MTIwNjQ2YQ==
https://www.instagram.com/reel/DHbHeavyTK5/?igsh=NTc4MTIwNjQ2YQ==
https://www.instagram.com/reel/DHbHDx0TBoU/?igsh=NTc4MTIwNjQ2YQ==
https://www.instagram.com/reel/DHbFGU3MeAs/?igsh=MWZreW93a2M4Y3hreg==
https://www.instagram.com/reel/DHbE8bFIRcA/?igsh=bWp5czN6b2I1eWRm
https://www.instagram.com/reel/DHdp0QOzC7l/?igsh=NTc4MTIwNjQ2YQ==
https://www.instagram.com/reel/DHdprmJzvKo/?igsh=NTc4MTIwNjQ2YQ==
https://www.instagram.com/reel/DHdp3y-zRCX/?igsh=NTc4MTIwNjQ2YQ==
https://www.instagram.com/reel/DHdp97oB-PX/?igsh=NTc4MTIwNjQ2YQ==
https://www.instagram.com/reel/DHdqCB3y8QA/?igsh=NTc4MTIwNjQ2YQ==
https://www.instagram.com/reel/DHfnKpPJGPz/?igsh=dDdmeDFvZTIxdnY4
https://www.instagram.com/reel/DHfnV88poBT/?igsh=MWtvbXRkOWlqcno3cQ==
https://www.instagram.com/reel/DHfnRkTzpA8/?igsh=MWE2bzNieWRxdmFrNg==
https://www.instagram.com/reel/DHfnf6qJxN1/?igsh=YzRtN3RwMTFmM3hn
https://www.instagram.com/reel/DHfnsJKzPvK/?igsh=NTc4MTIwNjQ2YQ==
https://www.instagram.com/reel/DHifkM0RYzu/?igsh=Y2lxa3JpODZuaG0z
https://www.instagram.com/reel/DHifxnuv4__/?igsh=QkFLSkFFZXRmQw%3D%3D
https://www.instagram.com/reel/DHif_JmSRMJ/?igsh=ZGhlZjZ5bDIxbGdj
https://www.instagram.com/reel/DHikGvWzYAp/?igsh=MTFoODJ1eTIzNWo2YQ==
https://www.instagram.com/reel/DHikPcVJldN/?igsh=emtyNDNwaTRkcXMz
https://www.instagram.com/reel/DHk2NELNY6z/?igsh=cmluZW1sdndxM2hx
https://www.instagram.com/share/reel/_wqnLi5jf
https://www.instagram.com/reel/DHk1vx0SCOr/?igsh=MXUzcHVrODk4bHM3OQ==
https://www.instagram.com/reel/DHk1PhvSiXX/?igsh=OGxxcXBxZjdjMmEy
https://www.instagram.com/reel/DHk1NNVPMgk/?igsh=MXZmZDQ1aHEwamY1cg==
https://www.instagram.com/reel/DHnvzIyyTiv/?igsh=MW82M214d2h6emFkeQ==
https://www.instagram.com/reel/DHnwfQuJJ0U/?igsh=YjNwZXVjbHQ3bWQ2
https://www.instagram.com/p/DHnv_Q6P7jA/
https://www.instagram.com/reel/DHnvwYRIB1o/?igsh=aXF3aGFzbDFkbHUw
https://www.instagram.com/reel/DHnwXW8M0n7/?igsh=dXoyMDR1ODU4dWxo
https://www.instagram.com/reel/DHp-K7Rophd/?igsh=YWRpbTMzYzVwNzRk
https://www.instagram.com/reel/DHp9zaYN0VH/?igsh=NXZxejJicHIxd2x3
https://www.instagram.com/reel/DHp9g16psgz/?igsh=MWVmcjRxdTR3NXg2cw==
https://www.instagram.com/reel/DHp957gzzbm/?igsh=NGxtZDgwOWNnajRr
https://www.instagram.com/reel/DHqAHG1T0Dg/?igsh=MWRlcXRueTE2cHcwNQ==
https://www.instagram.com/reel/DHslo75Cpda/?igsh=MTg2YWY1a3p3bjFhMQ==
https://www.instagram.com/reel/DHsmLEAzHeb/?igsh=MXdpOXpma3h5Z2o2ag==
https://www.instagram.com/reel/DHslm7xISrK/?igsh=MXJwM3NsOTkzYzAweA==
https://www.instagram.com/reel/DHsm59AimlF/?igsh=MW45eG54MTF3bzQ4Zw==
https://www.instagram.com/reel/DHsodcjxYBR/?igsh=YzF0amoweXYyb3h5
https://www.instagram.com/reel/DHvULjtP3_2/?igsh=MTJrYWY5OGZ1c2gwZw==
https://www.instagram.com/reel/DHvUp-jyTAi/?igsh=MXFjaXRybzZkZzRxNQ==
https://www.instagram.com/share/reel/BALWTp9-KA
https://www.instagram.com/reel/DHvVrdQTiet/?igsh=M2V6YzZlbGYyanYw
https://www.instagram.com/reel/DHva3S6y3TV/?igsh=c3Boc281M3d5N205
https://www.instagram.com/reel/DHyi3OTqnmG/?igsh=MXA1YXZ3NXFya2RoeA==
https://www.instagram.com/reel/DHyjVg0olbq/?igsh=N2FzZWxhdDR2aDl0
https://www.instagram.com/reel/DHyjgRAtYZa/?igsh=MW00NTJqaXFnem5hZQ==
https://www.instagram.com/reel/DHylagHTa75/?igsh=a3BlY3NtdHVzdXRr
https://www.instagram.com/reel/DHynLr1CMAa/?igsh=MW10emk3MWlnMWlvdw==
https://www.instagram.com/reel/DHbC-B3sG6w/?igsh=eXo2eXNwanhvZGNl
https://www.instagram.com/reel/DHdWl7bS6fe/?igsh=MTA3Z2lvNWo3d3N5YQ==
https://www.instagram.com/reel/DHftc8lxI4a/?igsh=aDQydzY4czUxYjl0
https://www.instagram.com/share/reel/_7t2SMxgB
https://www.instagram.com/reel/DHkxsibTD58/?igsh=b3BlcHFwdHphMnRh
https://www.instagram.com/reel/DHnm-7MyegI/?igsh=NHZ2czE4a2t5OWhz
https://www.instagram.com/reel/DHqGgjFPJCS/?igsh=dXhuMmNhOGZ3NGU0
https://www.instagram.com/reel/DHsoMRHpEjD/?igsh=MXZ4emNsYjIwY3BvNg==
https://www.instagram.com/reel/DHvTY8zBmYH/?igsh=MWhrbzBjbW1ycWdnMw==
https://www.instagram.com/share/reel/BAKQ50p1dF
https://www.instagram.com/reel/DHbPZwFvIQH/?igsh=MWRwa2Izcmt3amEzYQ==
https://www.instagram.com/reel/DHbQVrlta4K/?igsh=eHdjMDU1d3BtN3Ry
https://www.instagram.com/reel/DHbRX7Ko1bb/?igsh=emJqZHNvMDdsbDI3
https://www.instagram.com/share/reel/_xaifX9VG
https://www.instagram.com/reel/DHbR0kqNA8i/?igsh=M2JzcjcwZWtvdTY3
https://www.instagram.com/reel/DHbSs3PMnZS/?igsh=MXN2b2UzZm5tZ3J0MA==
https://www.instagram.com/reel/DHbSmHNSHWF/?igsh=MWxmM2gzZjB0bDZ4Zw==
https://www.instagram.com/reel/DHbRgG3Snhd/?igsh=MWU3cGg3bWEwZnc4NA==
"""

# Archive previous results
if os.path.exists('output/instagram_data_final_checked.xlsx'):
    shutil.copy('output/instagram_data_final_checked.xlsx', 'output/batch1_final.xlsx')
    print("Archived Batch 1 to output/batch1_final.xlsx")

# Update Input File
url_list = [u.strip() for u in urls.strip().split('\n') if u.strip()]
df = pd.DataFrame({'parsed_url': url_list})
df.to_excel('input/INSTAURL.xlsx', index=False, header=False) # No header as script expects raw urls usually or header?
# Let me check previous scripts... inspect_input_file.py said it had no header or 1 column. 
# scraper_new_input.py uses: df = pd.read_excel('input/INSTAURL.xlsx', header=None)
# So header=False is correct.

print(f"Updated input/INSTAURL.xlsx with {len(url_list)} URLs.")

# Cleanup Logs and Temp Output
if os.path.exists('logs_new'):
    for f in os.listdir('logs_new'):
        os.remove(os.path.join('logs_new', f))
    print("Cleared logs_new/ directory.")

if os.path.exists('output/instagram_data_new.xlsx'):
    os.remove('output/instagram_data_new.xlsx')
    print("Removed old output/instagram_data_new.xlsx.")

if os.path.exists('output/instagram_data_final.xlsx'):
    os.remove('output/instagram_data_final.xlsx')

if os.path.exists('output/instagram_data_final_checked.xlsx'):
    os.remove('output/instagram_data_final_checked.xlsx')

print("Ready for fresh scrape.")
