from __future__ import print_function
from place.automate.quanta_ray.QRay_driver import QuantaRay, QRread, QRstatus, QSW, QRcomm
from time import sleep
'''
Script demonstrating example communications with Quanta-Ray INDI, LAB, or PRO series laser.

@author: Jami L Johnson
September 5, 2014
'''

QuantaRay().openConnection()

print(QuantaRay().getID())

print('Amplifier PFN set to ', QRread().getAmpSetting())
print('Amplifier PFN power supply is actually ', QRread().getAmpPower())
print('Oscillator PFN set to ', QRread().getOscSetting())
print('Oscillator PFN power supply is actually ', QRread().getOscPower())
print('Q-Switch advanced sync setting: ', QSW().getAdv())
print('Q-Switch Adv: ', QRread().getAdv())
print('Q-Switch delay: ', QSW().getDelay())
print('Number of lamp shots: ', QRread().getShots())
print('shots 2:', QRread().getShots())
print('Lamp trigger rate: ', QRread().getTrigRate())
print('Laser status: ', QRstatus().getStatus())
print('Quanta-Ray help commands: ', QuantaRay().help())
print('Q-switch settings: ', QSW().get())
print('Setting QST to SING mode' )
#QSW().set(cmd='SING'))
print('Q-switch settings: ', QSW().get())
print('Q-switch advanced settings: ', QSW().getAdv())
print('current laser status: ', QRstatus().getStatus())
print('History buffer: ', QRstatus().getHist())
print('Questionable status: ', QRstatus().getQuest())
print('Set watchdog to', QRcomm().setWatchdog(time=100))
QuantaRay().on()
sleep(20)
QuantaRay().closeConnection()
