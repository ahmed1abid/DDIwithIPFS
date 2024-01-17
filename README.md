local_50# Decentalized Identity Management System

## How to use

### User

To open the command line interface of user ``python3 cli.py``
+ To initialize the user : use `(initialize | init) user` and enter the queried data to initialize an account:
   ```
   # DIMS> init user
     Enter your name: Alice Garcia
     Please give your wallet file path (will be created if not existing): ./wallet.yaml
     Enter your ssn: 121001
     
     Wallet Loaded 
     Hello Alice Garcia
   # Alice>
   ```
+ To show the current contents of the wallet, use `(display | show | view) wallet`.
  ```
  # Alice> display wallet
  ```
+ Since we do not have any certificates yet, the wallet is empty. Let's get some certificates now.

+ To setup the issuer from whom you want the certificate, use `set issuer`:
  ```
  # Alice> set issuer
  Enter the issuer from which you want a certificate: ABC University
  ```
  This will show the issuer details such as url, certificate schema, etc. if successful and create certificate for <b>ABC University</b>.
+ Now, you can view various details of the certificate issued by the company such as name or public key as:
```
# Alice> get certificate name
# Alice> get cert pkey
```
+ To obtain the certificate issued by the issuer, use `get (certificate | cert)`
  ```
  # Alice> get cert
  ```
  Now we have to wait while our issuer gathers up the details, makes the certificate, calculates the merkle root and signs it and sends it to be uploaded to the ethereum blockchain. 
  After this is done, use:
  ```
  # Alice> show wallet
  ```
  to view your newly obtained certificate!
+ Now we will use our newly obtained transcript from ABC University to apply for a job in <b>XYZ Company</b>. Execute:
  ```
  # Alice> set issuer
  Enter the issuer from which you want a certificate: XYZ Company
  ...
  # Alice> get cert
  ```
  You will be asked for various data needed by the company, some of which (marked as V) will be verified from the transcript. DIMS will automatically make a proof ensuring that only the fields required by the company are exposed and other fields are still private.
  
+ Again, we can use both of our certificates to get a loan certificate from the <b>SBI Bank</b>. Execute the following:
  ```
  # Alice> set issuer
  Enter the issuer from which you want a certificate: SBI Bank
  ...
  # Alice> get cert
  ```
+ Now that we have many certificates, we can view our wallet again to see all of them. 
  ```
  # Alice> show wallet
  ```
+ You can also view individual certificates by using `(display | show | view) (cert | certificate)` and enter the certificate to display that:
  ```
  # Alice> show cert
  ...
  Which one do you want to view? : loan
  ```

### Server

To open the command line interface of user 1``python3 issuer_cli.py``

+ To setup a Issuer : use `setup issuer` and enter the data - 
```
# DIMS> setup issuer
Enter Name: SBI Bank
Enter your port number: 8082
Enter your certificate name: loan
Enter database_name: sbi
Enter your requirements, and type 'done' when done:
Salary>10000
Requirement added: Salary>10000

Execute: python3 generated_SBI_Bank.py in future to run your Flask server
# SBI Bank> setup server
STARTING SERVER...
```



### IPFS 
generating ED25519 keypair...done
peer identity: 12D3KooWMyJNy5xxMPvPqtTpiRMfDAaHxWgPKgMe1RrpryP9ceaR
initializing IPFS node at /home/ahmed/.ipfs


### Documentation d'albastross/solo5/unipi : 

Long story short, the web server is a unipi unikernel, reproducible thanks to the ROBUR organisation, which retrieves its content from a remote git repository. The unikernel uses albatross for managing every unikernels and Solo5 as HVT ("hardware virtualized tender") tender. The remote github content is built automatically via a github action and uses Stapy for building static html pages. So I'd like to thank everyone who wrote any pieces of those softwares - they're really invaluable, well-written and totally useful!

Under the hood, what you basically want to do for seting up a similar architecture is:

    Get the unipi unikernel, albatross and solo5

    $ wget https://builds.robur.coop/job/unipi/build/..../f/bin/unipi.hvt
    $ wget https://builds.robur.coop/job/albatross/build/.../f/bin/albatross.deb
    $ wget https://builds.robur.coop/job/solo5/build/.../f/bin/solo5.deb
    $ sudo apt install albatross.deb solo5.deb -y

    Of course, you also should check the shasum hashes (they are on the builds.robur website) for validating you got unmodified binaries :)
    Create a tap interface for connecting your unikernel to the external world

    sudo mkdir -p /run/albatross/util/
    sudo chown albatross:albatross /run/albatross/util
    sudo systemctl start albatross_daemon
    sudo systemctl start albatross_consol
    sudo ip link add service type bridge
    sudo ip link set dev service-master master service
    sudo ip addr add 10.0.0.254/24 dev service
    sudo ip link set dev service up
    sudo sysctl -w net.ipv4.ip_forward=1
    sudo iptables -t nat -I POSTROUTING -s 10.0.0.0/24 -j MASQUERADE
    sudo iptables -t nat -I PREROUTING -p tcp --dport 8443 -j DNAT --to-destination 10.0.0.10

    Here 10.0.0.254 is our gateway for every unikernels, and we have to set a nat masquerade for allowing the unipi unikernel to retrieve the remote git content. The PREROUTING rule permit to redirect the incomming 8443 port to our unipi unikernel.
    Start the unikernel, telling him where to get the content

      sudo  albatross-client  create --net=service --mem=128       --arg="--ipv4=10.0.0.10/24" --arg="--ipv4-gateway=10.0.0.254"       --arg="--port=8443" --arg="--remote=s  "       --arg="--ssh-authenticator=SHA256:+DiY3wvvV6TuJJhbpZisF/zLDA0zPMSvHdkr4UvCOqU"       --arg="--ssh-key=ed25519:2JueTxGu7icIG6jpfFDl4AEr4L6zTUbMkS+e2vW4B/8="       --arg="--tls=false" --arg="--hook=/updatewebhook"       VMNAME unipi.hvt


    You can get the ssh-authenticator with the command: ssh-keygen -lf <(ssh-keyscan -t ed25519 remote-host 2>/dev/null). Your ssh-key is only needed if your repository isn't publicly visible (in the ed25519 format, you can use the tool awa_gen_key to produce a random seed and public key).
    Read the console logs and enjoy!

    $ albatross-client console VMNAME

Local (On Your Machine):

This part involves the initial setup and creating a certificate signing request (CSR) for your user.

    Generate the root CA certificate and server keypair:


albatross-client generate ca db

Create a signing request for your user:


albatross-client add_policy user 16 --mem 1024 --cpu 0 --cpu 1 --csr

Sign the user's request by the CA:

albatross-client sign cacert.pem db ca.key user.req


    Remote (On the Blockchain Node or Ganache CLI):

This part involves the creation of an Albatross VM using the signed user request.

    Create the Albatross VM:

 albatross-client create VMNAME 0xe4328460e96652d414a632c29c1034c6052c2510 --ca=user.pem --ca-key=user.pem --server-ca=cacert.pem --destination http://127.0.0.1:8545 --net=service --mem=128 --arg="--ipv4=10.0.0.10/24" --arg="--ipv4-gateway=10.0.0.254" --arg="--port=8443" --arg="--remote=https://github.com/ahmed1abid/DDIwithIPFS.git" --arg="--ssh-authenticator=SHA256:+DiY3wvvV6TuJJhbpZisF/zLDA0zPMSvHdkr4UvCOqU" --arg="--ssh-key=ed25519:2JueTxGu7icIG6jpfFDl4AEr4L6zTUbMkS+e2vW4B/8=" --arg="--tls=false" --arg="--hook=/updatewebhook"


npx ganache -d --gasLimit 8000000000000 --miner.callGasLimit 80000000000