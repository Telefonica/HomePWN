![Supported Python versions](https://img.shields.io/badge/python-3.6+-blue.svg?style=flat-square&logo=python)
![License](https://img.shields.io/badge/license-GNU-green.svg?style=flat-square&logo=gnu)

# **HomePwn - Swiss Army Knife for Pentesting of IoT Devices**

```
.__                         __________                
|  |__   ____   _____   ____\______   \__  _  ______  
|  |  \ /  _ \ /     \_/ __ \|     ___/\ \/ \/ /    \ 
|   Y  (  <_> )  Y Y  \  ___/|    |     \     /   |  \
|___|  /\____/|__|_|  /\___  >____|      \/\_/|___|  /
     \/             \/     \/                      \/ 


       ☠ HomePwn - IoT Pentesting & Ethical Hacking ☠                 

      Created with ♥  by: 'Ideas Locas (CDO Telefonica)'    
```

HomePwn is a framework that provides features to audit and pentesting devices that company employees can use in their day-to-day work and inside the same working environment. It is designed to find devices in the home or office, take advantage of certain vulnerabilities to read or send data to those devices. With a strong library of modules you can use this tool to load new features and use them in a vast variety of devices.

HomePwn has a modular architecture in which any user can expand the knowledge base about different technologies. Principally it has two different components:

* Discovery modules. These modules provide functionalities related to the discovery stage, regardless of the technology to be used. For example, it can be used to conduct WiFi scans via an adapter in monitor mode, perform discovery of BLE devices, Bluetooth Low-Energy, which other devices are nearby and view their connectivity status, etc. Also, It can be used to discover a home or office IoT services using protocols such as SSDP or Simple Service Discovery Protocol and MDNS or Multicast DNS.

* Specific modules for the technology to be audited. On the other hand, there are specific modules for audited technology. Today, HomePwn can perform auditing tests on technologies such as WiFi, NFC, or BLE. In other words, there are modules for each of these technologies in which different known vulnerabilities or different techniques are implemented to asses the device's security level implemented and communicated with this kind of technologies.

# Built With

* [Python](https://www.python.org/download/releases/3.0/) - Programming language used
* [Prompt Toolkit](https://python-prompt-toolkit.readthedocs.io/en/stable/) - Python command line

# Documentation

It's possible to read the documentation in our papers:
* [Spanish Version](https://github.com/ElevenPaths/HomePWN/blob/master/Papers/%5BPAPER%5D%20homepwn_ES_Version%20.pdf)
* [English Version](https://github.com/ElevenPaths/HomePWN/blob/master/Papers/%5BPAPER%5Dhomepwn_ENG.pdf)

# Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. See deployment for notes on how to deploy the project on a live system.

## Prerequisites:

You need to have Linux and python 3.6+ running in your computer, please install them in the download page.

* [Ubuntu](https://ubuntu.com/), [Debian](https://www.debian.org/) or similar.
* [Python 3.6+](https://www.python.org/downloads/).

## Installing all requisites:

To install all dependencies in Ubuntu 18.04 or derivatives use the file install.sh

```
> sudo apt-get update
> sudo ./install.sh
```
The script ask you if you want to create a virtualenv, if your answer is 'y' then it installs python libraries within the virtual environment, if not in the system itself

# Usage

To run the script, if you chose a virtual environment in the installation follow execute the next command to activate the virtual environment:

```
> source homePwn/bin/activate
```

Launch the application:

```
> sudo python3 homePwn.py
```

# Examples

Here are some videos to see how the tool works.

### **HomePwn. Bluetooth Low-Energy PoC & Hacking**
[![HomePwn. Bluetooth Low-Energy PoC & Hacking](https://img.youtube.com/vi/JgbIsP7IGxo/0.jpg)](https://www.youtube.com/watch?v=JgbIsP7IGxo)

### **HomePwn. Bluetooth Spoofing**
[![HomePwn. Bluetooth Spoofing](https://img.youtube.com/vi/o9P1BwlHelM/0.jpg)](https://www.youtube.com/watch?v=o9P1BwlHelM)

### **HomePwn. NFC Clone**
[![HomePwn. NFC Clone](https://img.youtube.com/vi/ZLas04ZCTLU/0.jpg)](https://www.youtube.com/watch?v=ZLas04ZCTLU)

### **HomePwn. BLE capture on PCAP file (sniffing)**
[![HomePwn. BLE capture on PCAP file (sniffing)](https://img.youtube.com/vi/vw9nr584PJQ/0.jpg)](https://www.youtube.com/watch?v=vw9nr584PJQ)

### **HomePwn. QR Options hack**
[![HomePwn. QR Options hack](https://img.youtube.com/vi/ta1DbnWOF8M/0.jpg)](https://www.youtube.com/watch?v=ta1DbnWOF8M)

### **HomePwn. Apple BLE Discovery**
[![HomePwn. Apple BLE Discovery](https://img.youtube.com/vi/xOU34op7Gls/0.jpg)](https://www.youtube.com/watch?v=xOU34op7Gls)

### **HomePwn. Xiaomi IoT Advertisement**
[![HomePwn. Xiaomi IoT Advertisement](https://img.youtube.com/vi/Xi7KZibJsfE/0.jpg)](https://www.youtube.com/watch?v=Xi7KZibJsfE)

# Authors

This project has been developed by the team of 'Ideas Locas' (CDO - Telefónica). To contact the authors:

* **Pablo Gonzázlez Perez** -- [@pablogonzalezpe](https://twitter.com/pablogonzalezpe) -- pablo.gonzalezperez@telefonica.com
* **Josué Encinar García** -- [@JosueEncinar](https://twitter.com/JosueEncinar) -- josue.encinargarcia@telefonica.com
* **Lucas Fernández Aragón** --  [@lucferbux](https://twitter.com/lucferbux) -- lucas.fernandezaragon@telefonica.com

See also the list of [CONTRIBUTORS.md](CONTRIBUTORS.md) who participated in this project.


# Contributing

Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct, and the process for submitting pull requests to us.


# License

This project is licensed under the GNU General Public License - see the [LICENSE.md](LICENSE.md) file for details.

# Disclaimer!

THE SOFTWARE (for educational purpose only) IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

This software doesn't have a QA Process.
