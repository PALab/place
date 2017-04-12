'''
This module tests the classes in the controller module.

All main classes of the controller module have a TestCLASSNAME class in this
module that contains one test_minimal function that gives an idea of the code
that is essential to use the respective class and one function test that is
more sophisticated.

Created on Jul 6, 2013

@author: henrik
'''
import unittest
import matplotlib.pyplot as plt
from place.automate.osci_card import controller

class Basic(unittest.TestCase):
    """
    test different controller for the ability to:
    - deal with a wrong order of configure functions
    - use the configureMode
    """
    def test_scrambledSetup(self):
        self.control.setTrigger(sourceOfJ="TRIG_CHAN_A", levelOfJ=128)
        self.control.createInput(inputRange="INPUT_RANGE_PM_100_MV", channel="CHANNEL_C")
        self.control.setSampleRate("SAMPLE_RATE_1KSPS")
        self.control.setTriggerTimeout(0.01)
        self.control.createInput(inputRange="INPUT_RANGE_PM_4_V")
        self.control.setSamplesPerRecord(postTriggerSamples=1024, preTriggerSamples=1024)
        self.control.setSampleRate("SAMPLE_RATE_10KSPS")
    def test_configMode(self):
        self.control.configureMode = True
        self.control.setTrigger(sourceOfJ="TRIG_CHAN_A", levelOfJ=128)     
        self.control.createInput(inputRange="INPUT_RANGE_PM_100_MV", channel="CHANNEL_C")  
        self.control.createInput(inputRange="INPUT_RANGE_PM_200_MV", channel="CHANNEL_D")  
        self.control.setSampleRate("SAMPLE_RATE_1KSPS")  
        self.control.setTriggerTimeout(0.01)
        self.control.createInput(inputRange="INPUT_RANGE_PM_4_V")  
        self.control.setSamplesPerRecord(postTriggerSamples=1024 , preTriggerSamples=1024)
        self.control.createInput(inputRange="INPUT_RANGE_PM_200_MV", channel="CHANNEL_B")  
        self.control.setSampleRate("SAMPLE_RATE_10KSPS")  
        self.control.configureMode = False
            
class TestTRSM(Basic):
    """
    use test from Basic for TriggeredRecordingSingleModeController
    """
    def setUp(self):
        self.control = TriggeredRecordingSingleModeController(debugMode=False)   
    def tearDown(self):
        self.control.startCapture()
        self.control.waitForEndOfCapture(0.23)
        self.control.readData()
        for key in self.control.data.keys():
            plt.plot(self.control.getDataAtOnce(key), label=key)
            plt.legend()
        plt.show()

class TestTR(Basic):
    """
    use test from Basic for TriggeredRecordingController
    """
    def setUp(self):
        self.control = TriggeredRecordingController(debugMode=True)   
    def tearDown(self):
        self.control.startCapture()
        self.control.readData()
        for key in self.control.data.keys():
            plt.plot(self.control.getDataAtOnce(key), label=key)
            plt.legend()
        plt.show()
        
class TestContinuousStreaming(unittest.TestCase):
    def test_minimal(self):
        control = ContinuousController()
        control.createInput()  
        control.setSampleRate("SAMPLE_RATE_1MSPS")
        control.startCapture()
        control.readData()
        times = control.getTimes()
        # plotting
        plt.title("One continuous stream of samples")
        plt.plot(times, control.getDataAtOnce("CHANNEL_A"), '.')
        plt.xlabel("time [s]")
        plt.ylabel("voltage [V]")
        plt.show()
    def test_speed(self):
        control = ContinuousController()
        control.createInput()  
        control.setSampleRate("SAMPLE_RATE_20MSPS")  # 20MSPS is the highes rate that could be achieved
        control.setNumberOfBuffers(2)
        control.setSamplesPerBuffer(1024 * 1024) 
        control.startCapture()
        control.readData()
        times = control.getTimes()
        # plotting
        plt.title("One continuous stream of samples")
        plt.plot(times, control.getDataAtOnce("CHANNEL_A"), '.')
        plt.xlabel("time [s]")
        plt.ylabel("voltage [V]")
        plt.show()
    def test(self):
        control = ContinuousController(debugMode=False)
        control.configureMode = True    
        control.createInput(inputRange="INPUT_RANGE_PM_100_MV")  
        control.createInput(channel="CHANNEL_B")
        control.setSampleRate("SAMPLE_RATE_1MSPS")
        control.setNumberOfBuffers(8)
        control.setSamplesPerBuffer(1024)
#        control.setSamplesPerBuffer(1024 * 1024) # select this to test a longer acquisition
        control.setCaptureDurationTo(0.2)
        control.configureMode = False
        control.startCapture()
        control.readData()
        times = control.getTimes()
        plt.plot(times, control.getDataAtOnce("CHANNEL_A"), '.')
        plt.plot(times, control.getDataAtOnce("CHANNEL_B"), '.')
        plt.show()
        
class TestTriggeredContinuousStreaming(unittest.TestCase):
    def test_minimal (self):
        control = TriggeredContinuousController()
        control.createInput()  
        control.setSampleRate("SAMPLE_RATE_100KSPS")
        control.setTrigger()
        control.setTriggerTimeout(0.1)
        control.startCapture()
        control.readData()
        times = control.getTimesOfRecord()
        records = control.getDataRecordWise("CHANNEL_A")
        # plotting
        fig = plt.figure()
        plt.subplots_adjust(hspace=.5)
        times = list(times)
        times = [-times[2], -times[1]] + times
        for i, record in enumerate(records):
            ax = fig.add_subplot(len(records) + 1, 1, i + 1)
            ax.plot(times, [0, 0] + record)
            ax.set_ylabel("voltage [V]")
        fakeTrig = control.postTriggerSamples * [1]
        fakeTrig = 2 * [-1] + fakeTrig
        ax = fig.add_subplot(len(records) + 1, 1, len(records) + 1)
        ax.plot(times   , fakeTrig, '-')
        ax.set_ylim((-1.5, 1.5))
        ax.set_ylabel("fake trigger signal [a.u.]")
        fig.canvas.set_window_title("Multiple Acquired Records without preTriggerSamples")
        plt.xlabel("time [s]")
        plt.show()

    def test (self):
        # Test TriggeredContinuousController
        control = TriggeredContinuousController(debugMode=False)
        control.configureMode = True    
        control.createInput(inputRange="INPUT_RANGE_PM_400_MV")  
        # control.createInput(channel="CHANNEL_B")
        control.setSampleRate("SAMPLE_RATE_100KSPS")
        control.setTrigger(sourceOfJ="TRIG_CHAN_A", levelOfJ=128)
        control.setTriggerTimeout(0.1)
        # control.setRecordsPerCapture(10)
        control.setRecordsPerBuffer(4, 4)
        # control.setCaptureDurationTo(1)
        control.setSamplesPerRecord(samples=4096)
        control.configureMode = False
        control.startCapture()
        control.readData()
        data = control.data
        times = control.getTimesOfCapture()
        # print len(data["CHANNEL_B"])        
        plt.plot(times, control.getDataAtOnce("CHANNEL_A"), '.')
        # plt.plot(data["CHANNEL_B"])
        plt.show()

class TestTriggeredRecordingController(unittest.TestCase):
    def test_minimal(self):
        control = TriggeredRecordingController()
        control.createInput()  
        control.setSampleRate("SAMPLE_RATE_100KSPS")
        control.setTrigger()
        control.setTriggerTimeout(0.1)
        control.setSamplesPerRecord(preTriggerSamples=2560, postTriggerSamples=2560)
        control.startCapture()
        control.readData()
        times = control.getTimesOfRecord()
        records = control.getDataRecordWise("CHANNEL_A")
        # plotting
        fig = plt.figure()
        plt.subplots_adjust(hspace=.5)
        for i, record in enumerate(records):
            ax = fig.add_subplot(len(records) + 1, 1, i + 1)
            ax.plot(times, record)
            ax.set_ylabel("voltage [V]")
        fakeTrig = control.preTriggerSamples * [-1] + control.postTriggerSamples * [1]
        ax = fig.add_subplot(len(records) + 1, 1, len(records) + 1)
        ax.plot(times, fakeTrig, '-')
        ax.set_ylim((-1.5, 1.5))
        ax.set_ylabel("fake trigger signal [a.u.]")
        fig.canvas.set_window_title("Multiple Acquired Records with preTriggerSamples")
        plt.xlabel("time [s]")
        plt.show()
        
    def test(self):
        control = TriggeredRecordingController(debugMode=False)
        control.configureMode = True    
        control.createInput(inputRange="INPUT_RANGE_PM_400_MV")  
        control.createInput(channel="CHANNEL_B")
        control.setSampleRate("SAMPLE_RATE_10KSPS")
        control.setTrigger(sourceOfJ="TRIG_CHAN_A", levelOfJ=128)
        control.setTriggerTimeout(0.11)
        control.configureMode = False
        control.startCapture()
        control.readData()
        times = control.getTimesOfCapture()
        control.saveDataToTextFile("hallo.txt", "CHANNEL_A")
        control.saveDataToNumpyFile("hallo.txt", "CHANNEL_A")
        plt.plot(times, control.getDataAtOnce("CHANNEL_A"), '.')
        plt.plot(times, control.getDataAtOnce("CHANNEL_B"), '.')
        plt.show()

class TestBasicController(unittest.TestCase):
    def test_minimal (self):
        control = BasicController()
        control.enableLED()
        import time
        time.sleep(5)
        control.disableLED()
    def test(self):
        control = BasicController()
        control.configureMode = True    
        control.setSampleRate("SAMPLE_RATE_10KSPS")
        control.createInput()
        control.configureMode = False

def load_tests(loader, test_cases):
    suite = unittest.TestSuite()
    for test_class in test_cases:
        tests = loader.loadTestsFromTestCase(test_class)
        suite.addTests(tests)
    return suite


if __name__ == "__main__":
    # unittest.main()
    all_test_cases = (TestContinuousStreaming, TestTriggeredContinuousStreaming, TestTR, TestTriggeredRecordingController, TestTRSM, TestBasicController)
    all_test_cases = (TestTriggeredContinuousStreaming, TestBasicController)
    all_suite = load_tests(unittest.TestLoader(), all_test_cases)
    default_suite = unittest.TestSuite()
    default_suite.addTest(TestContinuousStreaming('test_minimal'))
    default_suite.addTest(TestTriggeredContinuousStreaming('test_minimal'))
    default_suite.addTest(TestTriggeredRecordingController('test_minimal'))
    default_suite.addTest(TestBasicController('test_minimal'))
    unittest.TextTestRunner(verbosity=2).run(default_suite)
#    unittest.TextTestRunner(verbosity=2).run(all_suite)
     
