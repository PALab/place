"""Driver module for Newport's Spectra-Physics Quanta-Ray INDI, PRO, and LAB
Series Nd:YAG lasers.

NOTE: the watchdog parameter is important!  The laser will turn off if it does
not receive a command within the watchdog time period.  Therefore, it is
advised to use a command like QRstatus().get_status() at regular intervals to
query the status of the laser during operation.

@author: Jami L Johnson
September 5, 2014
"""
import serial

class QuantaRay:
    """QuantaRay class"""
    def __init__(self, portINDI='/dev/ttyUSB0', baudINDI=9600):
        """Define serial port for INDI"""
        self.indi = serial.Serial(
            port=portINDI,
            baudrate=baudINDI,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_TWO,
            bytesize=serial.EIGHTBITS,
            timeout=1
            )

    def open_connection(self):
        """ Open serial connection to INDI"""
        self.indi.close()
        self.indi.open()
        indi_open = self.indi.isOpen()
        if indi_open is False:
            raise RuntimeError('unable to connect to INDI')

    def close_connection(self):
        """Close connection to INDI"""
        self.indi.close()

    def get_id(self):
        """Get ID"""
        self.indi.write('*IDN?\r'.encode())
        return self.indi.readline().decode()

    def help(self):
        """Prints serial command options (operational commands)"""
        self.indi.write('HELP\r'.encode())
        for _ in range(1, 6):
            print(self.indi.readline().decode())

    def turn_on(self):
        """Turns Quanta-Ray INDI on"""
        self.indi.write('ON\r'.encode())

    def turn_off(self):
        """Turns Quanta-Ray INDI off"""
        self.indi.write('OFF\r'.encode())

    def set_lamp(self, lamp_set='FIX', lamp_pulse=''):
        """Select lamp trigger source

        lamp_set:
        FIX = set lamp trigger to Fixed
        EXT = set lamp trigger to External Source
        VAR = set lamp trigger to Variable
        INH = inhibit lamp trigger

        lamp_pulse = set rate of lamp (pulses/second)
        """
        if lamp_pulse != '':
            self.indi.write(('LAMP '+ str(lamp_set) + ' ' + str(lamp_pulse) + '\r').encode())
        else:
            self.indi.write(('LAMP '+ str(lamp_set) + '\r').encode())

    def get_lamp(self):
        """ Returns the lamp Variable Rate trigger setting """
        self.indi.write('LAMP VAR?\r'.encode())
        return self.indi.readline().decode()

    def set(self, cmd='NORM'):
        """Set mode, type, or timing of Q-switch

        cmd:
        LONG = long pulse mode
        EXT = external mode
        NORM = normal mode
        SING = single shot
        FIR = fire Q-switch once
        REP = repetitive shots
        """
        self.indi.write(('QSW ' + str(cmd) + '\r').encode())

    def single_shot(self):
        """Set single shot"""
        self.set('SING')

    def normal_mode(self):
        """Set normal mode"""
        self.set('NORM')

    def repeat_mode(self, watchdog_timeout):
        """Set repetitive shots and ensures watchdog is turned on (not disabled)

        :param watchdog_timeout: seconds before laser safety shutoff
        :type watchdog_timeout: int

        #:raises ValueError: if watchdog is requested to be 0 (disabled)
        """
        if watchdog_timeout == 0:
            dummy = input('QuantaRay INDI Laser watchdog is 0 s. This will ' +
                          'disable watchdog and the laser will continue to run ' +
                          'after the experiment has finished. Continue? [ y / n ]:')
            if dummy == 'n':
                raise ValueError('Disabling watchdog when using repeat mode is not advised')
        self.set_watchdog(watchdog_timeout)
        self.set('REP')

    def get(self):
        """Queries and returns the Q-switch settings."""
        self.indi.write('QSW?\r'.encode())
        return self.indi.readline().decode()

    def set_adv(self, delay):
        """Set advanced sync delay"""
        self.indi.write(('ADV ' + str(delay) + '\r').encode())

    def get_adv(self):
        """Queries and returns the Q-switch Advanced Sync settings"""
        self.indi.write('QSW ADV? \r'.encode())
        return self.indi.readline().decode()

    def set_delay(self, delay):
        """Sets delay for Q-switch delay"""
        self.indi.write(('QSW DEL ' + str(delay) + '\r').encode())

    def get_delay(self):
        """Queries and returns the Q-switch delay setting"""
        self.indi.write('QSW DEL? \r'.encode())
        return self.indi.readline().decode()

    def set_echo(self, mode=0):
        """Set echo mode of INDI.

        mode:
        0 = show prompts
        1 = laser echoes characters as received
        2 = shows error messages
        3 = output line feed for every command (even those that don't normally generate a response)
        4 = terminate responses with <cr><lf>, rather than just <lf>
        5 = use XON/XOFF handshaking for data sent to laser (not for data sent from the laser)
        """
        self.indi.write(('ECH ' + str(mode) + '\r').encode())

    def set_watchdog(self, time=10):
        """Set range of watchdog. If the laser does not receive communication
        from the control computer within the specifiedc time, it turns off. If
        disabled, the default time is zero. Time must be between 0 and 110
        seconds.
        """
        if time < 0 or time > 110:
            raise ValueError('Invalid watchdog time. Choose value between 0 and 110 seconds.')
        self.indi.write(('WATC ' + str(time) + '\r').encode())

    def set_baud(self, baud_indi=9600):
        """Sets baudrate of laser. At power-up, baudrate is always 9600."""
        self.indi.write(('BAUD ' + str(baud_indi) + '\r').encode())

    def get_amp_setting(self):
        """Queries amplifier PFN command setting in percent"""
        self.indi.write('READ:APFN?\r'.encode())
        return self.indi.readline().decode()

    def get_amp_power(self):
        """Queries amplifier PFN monitor in percent (what PFN power supply is actually doing)"""
        self.indi.write('READ:AMON?\r'.encode())
        return self.indi.readline().decode()

    def get_osc_setting(self):
        """Queries oscillator PFN command setting in percent"""
        self.indi.write('READ:OPFN?\r'.encode())
        return self.indi.readline().decode()

    def get_osc_power(self):
        """Queries oscillator PFN monitor in percent (what PFN power supply is actually doing)"""
        self.indi.write('READ:OMON?\r'.encode())
        return self.indi.readline().decode()

    def get_qsw_adv(self):
        """Queries and returns the current Q-Switch Advanced Sync setting"""
        self.indi.write('READ:QSWADV?\r'.encode())
        return self.indi.readline().decode()

    def get_shots(self):
        """Queries and returns the number of shots"""
        self.indi.write('SHOT?\r'.encode())
        return self.indi.readline().decode()

    def get_trig_rate(self):
        """Queries and returns the lamp trigger rate (unless lamp trigger source is external"""
        self.indi.write('READ:VAR?\r'.encode())
        return self.indi.readline().decode()

    def set_osc_power(self, percent=0):
        """set the Oscillator PFN voltage as a percentage of factory full scale"""
        self.indi.write(('OPFN ' + str(percent) + '\r').encode())

    def set_amp_power(self, percent=0):
        """set the PFN Amplifier voltage as a percentage of factory full scale"""
        self.indi.write(('APFN ' + str(percent) + '\r').encode())

    def get_status(self):
        """Returns the laser status.

        Result is a list with entries of the form: [bit, error], where "bit" is
        the bit of the status byte, and "error" is a text description of the
        error.
        """

        attempts, responses = 0, []
        while attempts < 3:
            try:
                self.indi.write('*STB?\r'.encode())
                response = self.indi.readline().decode()
                stb_value = bin(int(response))
                stb_value = stb_value[2:] # remove 0b at beginning
                #print 'stb_value: ', stb_value # prints binary status byte value
                break
            except ValueError:
                attempts += 1
                responses.append(response)
        else:
            print("Responses received from INDI:", responses)
            raise RuntimeError("Cannot retrieve status from INDI. This may be a connection or startup issue.")

        error_list = list()

        if stb_value[len(stb_value)-1] == '1':
            bit = '0'
            error = 'Laser emission can occur'
            stat = [bit, error]
            error_list.append(stat)
        if stb_value[len(stb_value)-2] == '1':
            bit = '1'
            error = 'Reserved error'
            stat = [bit, error]
            error_list.append(stat)
        if stb_value[len(stb_value)-3] == '1':
            bit = '2'
            error = ('Data is in the error log.\n'
                     + '(use QRstatus().getHist() for details on the error.)')
            stat = [bit, error]
            error_list.append(stat)
        if stb_value[len(stb_value)-4] == '1':
            bit = '3'
            error = 'Check QRstatus().getQuest() for error'
            stat = [bit, error]
            error_list.append(stat)
        if stb_value[len(stb_value)-5] == '1':
            bit = '4'
            error = 'Reserved error'
            stat = [bit, error]
            error_list.append(stat)
        if stb_value[len(stb_value)-6] == '1': #5 **********
            bit = '5'
            error = 'Check *ESR bits for error.'
            stat = [bit, error]
            error_list.append(stat)
        if stb_value[len(stb_value)-7] == '1':
            bit = '6'
            error = 'Reserved error'
            stat = [bit, error]
            error_list.append(stat)
        if stb_value[len(stb_value)-8] == '1': #7 ****
            bit = '7'
            error = 'Check STR:OPER bits'
            stat = [bit, error]
            error_list.append(stat)
        if stb_value[len(stb_value)-9] == '1':
            bit = '8'
            error = 'Main contactor is energized'
            stat = [bit, error]
            error_list.append(stat)
        if stb_value[len(stb_value)-10] == '1':
            bit = '9'
            error = 'Oscillator simmer is on'
            stat = [bit, error]
            error_list.append(stat)
        if stb_value[len(stb_value)-11] == '1':
            bit = '10'
            error = 'Amplifier simmer is on'
            stat = [bit, error]
            error_list.append(stat)
        if stb_value[len(stb_value)-12] == '1':
            bit = '11'
            error = 'Oscillator PFN is at target'
            stat = [bit, error]
            error_list.append(stat)
        if stb_value[len(stb_value)-13] == '1':
            bit = '12'
            error = 'The laser has recently fired'
            stat = [bit, error]
            error_list.append(stat)
        if stb_value[len(stb_value)-14] == '1':
            bit = '13'
            error = '15 Vdc power supply failure'
            stat = [bit, error]
            error_list.append(stat)
        if stb_value[len(stb_value)-15] == '1':
            bit = '14'
            error = 'Laser cover interlock open'
            stat = [bit, error]
            error_list.append(stat)
        if stb_value[len(stb_value)-16] == '1':
            bit = '15'
            error = ('Interlock open: CDRH plug, power supply cover, laser '
                     + 'head cover, laser head temperature, water pressure, '
                     + 'or water flow')
            stat = [bit, error]
            error_list.append(stat)
        if stb_value[len(stb_value)-17] == '1':
            bit = '16'
            error = 'Remote panel disconnected'
            stat = [bit, error]
            error_list.append(stat)
        if stb_value[len(stb_value)-18] == '1':
            bit = '17'
            error = 'Internal 208 Vac failure'
            stat = [bit, error]
            error_list.append(stat)
        if stb_value[len(stb_value)-19] == '1':
            bit = '18'
            error = 'CDRH enable failure'
            stat = [bit, error]
            error_list.append(stat)
        if stb_value[len(stb_value)-20] == '1':
            bit = '19'
            error = 'Laser ID fault'
            stat = [bit, error]
            error_list.append(stat)
        if stb_value[len(stb_value)-21] == '1':
            bit = '20'
            error = 'Low water fault'
            stat = [bit, error]
            error_list.append(stat)
        if stb_value[len(stb_value)-22] == '1':
            bit = '21'
            error = 'Interlock fault'
            stat = [bit, error]
            error_list.append(stat)
        if stb_value[len(stb_value)-23] == '1':
            bit = '22'
            error = 'Remote panel connected'
            stat = [bit, error]
            error_list.append(stat)
        if stb_value[len(stb_value)-24] == '1':
            bit = '23'
            error = 'Remote panel indicates that the computer is in control.'
            stat = [bit, error]
            error_list.append(stat)
        if len(stb_value) > 24:
            if stb_value[len(stb_value)-25] == '1':
                bit = '24'
                error = 'Main contactor should be on.'
                stat = [bit, error]
                error_list.append(stat)
            if stb_value[len(stb_value)-26] == '1':
                bit = '25'
                error = 'Reserved error'
                stat = [bit, error]
                error_list.append(stat)
            if stb_value[len(stb_value)-27] == '1':
                bit = '26'
                error = 'Reserved error'
                stat = [bit, error]
                error_list.append(stat)
            if stb_value[len(stb_value)-28] == '1':
                bit = '27'
                error = 'Reserved error'
                stat = [bit, error]
                error_list.append(stat)
            if stb_value[len(stb_value)-29] == '1':
                bit = '28'
                error = 'Reserved error'
                stat = [bit, error]
                error_list.append(stat)
            if stb_value[len(stb_value)-30] == '1':
                bit = '29'
                error = 'Reserved error'
                stat = [bit, error]
                error_list.append(stat)
            if stb_value[len(stb_value)-31] == '1':
                bit = '30'
                error = 'Reserved error'
                stat = [bit, error]
                error_list.append(stat)
            if stb_value[len(stb_value)-31] == '1':
                bit = '32'
                error = 'Reserved error'
                stat = [bit, error]
                error_list.append(stat)
        return error_list

    def get_quest(self):
        """Returns questionable condition register.

        Result is a list with entries of the form: [bit, error], where "bit" is
        the bit of the status byte, and "error" is a text description of the
        error.
        """
        self.indi.write('STAT:QUES?\r'.encode())

        qb_value = bin(int(self.indi.readline().decode()))
        qb_value = qb_value[3:]

        error_list = list()
        #print 'qb_value: ', qb_value # prints binary STAT:QUES? value

        if qb_value[len(qb_value)-1] == '1':
            bit = '0'
            error = '-Reserved error'
            stat = [bit, error]
            error_list.append(stat)
        if qb_value[len(qb_value)-2] == '1':
            bit = '1'
            error = '-Reserved error'
            stat = [bit, error]
            error_list.append(stat)
        if qb_value[len(qb_value)-3] == '1':
            bit = '2'
            error = '-Reserved error'
            stat = [bit, error]
            error_list.append(stat)
        if qb_value[len(qb_value)-4] == '1':
            bit = '3'
            error = '-Reserved error'
            stat = [bit, error]
            error_list.append(stat)
        if qb_value[len(qb_value)-5] == '1':
            bit = '4'
            error = '-Reserved error'
            stat = [bit, error]
            error_list.append(stat)
        if qb_value[len(qb_value)-6] == '1':
            bit = '5'
            error = '-Reserved error'
            stat = [bit, error]
            error_list.append(stat)
        if qb_value[len(qb_value)-7] == '1':
            bit = '6'
            error = '-Reserved error'
            stat = [bit, error]
            error_list.append(stat)
        if qb_value[len(qb_value)-8] == '1':
            bit = '7'
            error = '-Reserved error'
            stat = [bit, error]
            error_list.append(stat)
        if qb_value[len(qb_value)-9] == '1':
            bit = '8'
            error = '-Reserved error'
            stat = [bit, error]
            error_list.append(stat)
        if qb_value[len(qb_value)-10] == '1':
            bit = '9'
            error = '-Oscillator HV failure'
            stat = [bit, error]
            error_list.append(stat)
            QuantaRay().turn_off()
            exit()
        if qb_value[len(qb_value)-11] == '1':
            bit = '10'
            error = '-Amplifier HV failure'
            stat = [bit, error]
            error_list.append(stat)
        if qb_value[len(qb_value)-12] == '1':
            bit = '11'
            error = '-External trigger rate out of range.'
            stat = [bit, error]
            error_list.append(stat)
        if qb_value[len(qb_value)-13] == '1':
            bit = '12'
            error = '-De-ionized water low'
            stat = [bit, error]
            error_list.append(stat)
        if len(qb_value) > 15:
        # bits 13-15 undefined
            if qb_value[len(qb_value)-17] == '1':
                bit = '16'
                error = '-OSC HVPS # 1 EndOfCharge'
                stat = [bit, error]
                error_list.append(stat)
            if qb_value[len(qb_value)-18] == '1':
                bit = '17'
                error = '-OverLoad'
                stat = [bit, error]
                error_list.append(stat)
            if qb_value[len(qb_value)-19] == '1':
                bit = '18'
                error = '-OverTemp'
                stat = [bit, error]
                error_list.append(stat)
            if qb_value[len(qb_value)-20] == '1':
                bit = '19'
                error = '-OverVolt'
                stat = [bit, error]
                error_list.append(stat)
            if qb_value[len(qb_value)-21] == '1':
                bit = '20'
                error = '-OSC HVPS #2 EndOfCharge'
                stat = [bit, error]
                error_list.append(stat)
            if qb_value[len(qb_value)-22] == '1':
                bit = '21'
                error = '-OverLoad'
                stat = [bit, error]
                error_list.append(stat)
            if qb_value[len(qb_value)-23] == '1':
                bit = '22'
                error = '-OverTemp'
                stat = [bit, error]
                error_list.append(stat)
            if qb_value[len(qb_value)-24] == '1':
                bit = '23'
                error = '-OverVolt'
                stat = [bit, error]
                error_list.append(stat)
            if qb_value[len(qb_value)-25] == '1':
                bit = '24'
                error = '-AMP HVPS # 1 EndOfCharge'
                stat = [bit, error]
                error_list.append(stat)
            if qb_value[len(qb_value)-26] == '1':
                bit = '25'
                error = '-OverLoad'
                stat = [bit, error]
                error_list.append(stat)
            if qb_value[len(qb_value)-27] == '1':
                bit = '26'
                error = '-OverTemp'
                stat = [bit, error]
                error_list.append(stat)
            if qb_value[len(qb_value)-28] == '1':
                bit = '27'
                error = '-OverVolt'
                stat = [bit, error]
                error_list.append(stat)
            if qb_value[len(qb_value)-29] == '1':
                bit = '28'
                error = '-AMP HVPS # 2 EndOfCharge'
                stat = [bit, error]
                error_list.append(stat)
            if qb_value[len(qb_value)-30] == '1':
                bit = '29'
                error = '-OverLoad'
                stat = [bit, error]
                error_list.append(stat)
            if qb_value[len(qb_value)-31] == '1':
                bit = '30'
                error = '-OverTemp'
                stat = [bit, error]
                error_list.append(stat)
            if qb_value[len(qb_value)-32] == '1':
                bit = '31'
                error = '-OverVolt'
                stat = [bit, error]
                error_list.append(stat)
        return error_list

    def reset(self):
        """ Resets the laser head PC board"""
        self.indi.write('*RST?\r'.encode())
        print('Laser PC board reset')

    def get_hist(self):
        """Returns up to 16 status/error codes from the system history buffer.
        Use if the laser has shut off or the system is behaving erratically.
        The first element is the most recent.
        Example output:
        1 827 # 1 error has occured, current time is 827 sec
        301 801 # Error code 301 occured at 810 seconds
        0 0 # End of history buffer
        """
        self.indi.write('READ:HIST?\r'.encode())
        reply = '1'
        reply_list = list()
        while reply[0] != '0': #end of history buffer
            reply = self.indi.readline().decode().rstrip()
            reply_list.append(reply)
        return reply_list
