import numpy as np
import numpy.fft as fft
import matplotlib.pyplot as plt
from obspy.core import read
from obspy import Trace, Stream
import csv 
import scipy.signal

'''
    Module for plotting stream produced by pyPAL automation.  Data must be in H5 format. 
    
    Example usage:
    
         from obspy.core import read
         from obspy import Stream
         from PALplots import wiggle, contour, fk, fkfilter
    
         stream = read('PA_2.h5', format='H5', apply_calib=True)

         wiggle(stream, percent=50)
         contour(stream)
         fk(stream)
         fkfilter(stream,spread=7,colormap='gray')

    May 27, 2014
    @author: Jami Johnson
'''   

def wiggle(stream, dx = 1, percent=100, output='points.csv'):
    '''
    Creates plot of traces ("wiggles") vs. position from an ObsPy stream produced by pyPAL.  
    The positive peaks of each wiggle are filled.

    Parameters: 
         stream : ObsPy stream created with custom header information by pyPAL.  Required header information: delta, npts, position, position_unit
         dx : spacing between wiggles.  For example, dx = 10 will plot every tenth trace 
         percent : percent of maximum amplitude for each trace.  A value of 100 plots the full amplitude of the (normalized) traces, a value of 50 clips data with an amplitude greater than 50% of the maximum amplitude in the trace. 
         output : name of file to save 'picked' points to. Saves by default to 'points.csv'
    '''

    global px,py,ax
    
    px = [] #array of picked x-values
    py = [] #array of picked y-values
    
    newstream = stream.copy() # create copy of stream to manipulate
   
    newstream.detrend('demean') # remove DC trend
    percent/=100.

    # remove time_delay due to decoder
    if newstream[0].stats.time_delay > 0:
        for trace in newstream:
            trim_i = trace.stats.time_delay*1e-6/trace.stats.delta
            trace.data = trace.data[trim_i:]
   
    inc = newstream[1].stats.position - newstream[0].stats.position # spacing between receiver positions

    for trace in newstream: # clip data by specified percent of maximum amplitude
        trace.data = np.clip(trace.data,-max(trace.data)*percent,max(trace.data)*percent)
        trace.normalize()
        trace.data = trace.data*inc

    times = np.arange(0,newstream[0].stats.npts*newstream[0].stats.delta, newstream[0].stats.delta)*1e6
    
    fig = plt.figure()
    ax = fig.add_subplot(111)
    
    for i in range(0,len(newstream),dx):
        trace = newstream[i].data + newstream[i].stats.position # arrange to plot vs position
        position = [newstream[i].stats.position]*newstream[i].stats.npts
        ax.plot(trace, times, color='black',picker=True) # plot traces

        # fill under positive peaks
        if newstream[1].stats.position > newstream[0].stats.position:
            ax.fill_betweenx(times,trace, newstream[i].stats.position, where=trace>newstream[i].stats.position,color='black')
        elif newstream[1].stats.position < newstream[0].stats.position:
            ax.fill_betweenx(times,trace, newstream[i].stats.position, where=trace<newstream[i].stats.position,color='black') 
        
    plt.xlim((newstream[0].stats.position-inc,newstream[len(newstream)-1].stats.position+inc))
    plt.ylim((newstream[0].stats.npts*newstream[0].stats.delta*1e6,0))
    plt.xlabel('Position('+str(newstream[0].stats.position_unit)+')')
    plt.ylabel('Time ($\mu$s)')
    fig.canvas.mpl_connect('button_press_event', picker) # select/remove point
    plt.show()
    
    # write points to file
    if len(px) > 0:
        with open(output,'wb') as csvfile:
            outfile = csv.writer(csvfile, delimiter=',')
            outfile.writerow(px)
            outfile.writerow(py)

def contour(stream, output='points.csv', colormap='seismic'):
    '''
    Creates 2D image of stream data produced by pyPAL.  

    Parameters: 
         stream : ObsPy stream created with custom header information by pyPAL.  Required header information: delta, npts, position, position_unit
         colormap : choose colorscheme to display data (e.g. 'jet', 'gray', 'seismic')
         output : name of file to save 'picked' points to. Saves by default to 'points.csv'
    '''

    global px,py,ax

    px = []
    py = []
   
    # remove time_delay due to decoder
    if stream[0].stats.time_delay > 0:
        for trace in stream:
            trim_i = trace.stats.time_delay*1e-6/trace.stats.delta
            trace.data = trace.data[trim_i:]
    
    array = np.rot90(np.array(stream),1)

    fig, ax = plt.subplots()
    plt.imshow(array,extent=[stream[0].stats.position,stream[len(stream)-1].stats.position,0,stream[0].stats.npts*stream[0].stats.delta*1e6],aspect='auto',cmap=colormap,picker=True)
    ax.autoscale(False)
    plt.gca().invert_yaxis()
    cbar = plt.colorbar()
    if stream[0].stats.calib_unit.rstrip() == 'nm/V':
        cbar.set_label('Displacement (nm)')
    elif stream[0].stats.calib_unit.rstrip() == 'mm/s/V':
        cbar.set_label('Particle Velocity (mm/s)')
    plt.ylabel('Time ($\mu$s)')
    plt.xlabel('Scan Location ('+stream[0].stats.position_unit+')')
    fig.canvas.mpl_connect('button_press_event', picker) # pick point
    plt.show()

    # write picked points to file
    if len(px) > 0:
        with open(output,'wb') as csvfile:
            outfile = csv.writer(csvfile, delimiter=',')
            outfile.writerow(px)
            outfile.writerow(py)

def fk(stream, output='points.csv'):
    '''
    Plots frequency-wavenumber spectrum for stream recorded by pyPAL Scan.py.
    Parameters:
         stream : ObsPy stream created with custom header information defined by Scan.py.  Required header information: delta, npts, position.
         output : filename that selected velocity points are saved to.
    Use left-click to select points.  Each point defines a line with the origin with a slope 1/velocity.  This velocity is displayed when point is chosen.
    To remove a point, right click.
    '''

    global px, py, ax

    px = [] # array of picked frequency values 
    py = [] # array of picked wavenumber values

    nx = len(stream)
    nt = stream[0].stats.npts
    nk = 2*nx
    nf = 2*nt
    dx = stream[1].stats.position-stream[0].stats.position
    dt = stream[0].stats.delta

    stream_fft = fft.fftshift(fft.fft2(stream,s=[nk,nf])) #zero padded
    stream_psd2D = np.abs(stream_fft)**2 #2D power spectrum
    stream_psd2D = np.rot90(stream_psd2D,1)
    
    fig, ax = plt.subplots()
    plt.imshow(np.log10(stream_psd2D),extent=[-1/(2*dx),1/(2*dx),-1e-6/(2*dt),1e-6/(2*dt)],aspect='auto',cmap = 'gray',picker=True)
    ax.autoscale(False)
    plt.ylim((0,1e-6/(2*dt)))
    plt.ylabel('Frequency (MHz)')
    plt.xlabel('Spatial Frequency (1/mm)')
    fig.canvas.mpl_connect('button_press_event', pickV) # pick/remove points
    plt.show()

    if len(px) > 0:
        with open(output,'wb') as csvfile:
            outfile = csv.writer(csvfile, delimiter=',')
            outfile.writerow(px)
            outfile.writerow(py)

def fkfilter(stream, spread=7, colormap='seismic',output='points.csv'):
    '''
    Creates frequency-wavenumber filter of stream data produced by pyPAL. 
    Parameters:
         stream : ObsPy stream created with custom header information defined by Scan.py.  Required header information: delta, npts, position.
         spread : size of smoothing average kernel used to smooth the filter edges.
         colormap : colormap to use to display filtered data in the time domain.
         output : filename that selected velocity points are saved to.
    First, FK spectrum is displayed.
         Use left-click to select points.  Each point defines a line with the origin with a slope 1/velocity.  This velocity is displayed when point is chosen.
         To remove a point, right click.  Exactly two points must be selected to define the filter.  
         Press 'enter' when satisfied with the location of the velocity points.  
    Next, the FK filter will be displayed. 
    When FK filter figure is closed, the filtered data is displayed.
    '''

    global px, py, ax

    px = []  # array of picked frequency values 
    py = [] # array of picked wavenumber values

    nx = len(stream)
    nt = stream[0].stats.npts
    nk = 2*nx
    nf = 2*nt
    dx = stream[1].stats.position-stream[0].stats.position
    dt = stream[0].stats.delta

    stream_fft = fft.fftshift(fft.fft2(stream,s=[nk,nf])) # zero padded fft
    stream_psd2D = np.abs(stream_fft)**2 # 2D power spectrum for plotting
    stream_psd2D = np.rot90(stream_psd2D,1)

    fig, ax = plt.subplots()
    plt.imshow(np.log10(stream_psd2D),extent=[-1/(2*dx),1/(2*dx),-1e-6/(2*dt),1e-6/(2*dt)],aspect='auto',cmap = 'gray',picker=True)
    ax.autoscale(False)
    plt.ylim((0,1e-6/(2*dt)))
    plt.ylabel('Frequency (MHz)')
    plt.xlabel('Spatial Frequency (1/mm)')
    fig.canvas.mpl_connect('button_press_event', pickV) # pick/remove points
    fig.canvas.mpl_connect('key_press_event', submitV) # submit points
    plt.show()

    if (py[0]/px[0]) > (py[1]/px[0]):
        vmin = (py[1]/px[0])*1e3
        vmax = (py[0]/px[0])*1e3
    else: 
        vmin = (py[0]/px[0])*1e3
        vmax = (py[1]/px[1])*1e3

    # create fk filter
    H = np.zeros((nk,nf))
    f = -np.arange(-nf/2,nf/2,1)/(nf*dt)
    k = np.arange(-nk/2,nk/2,1)/(nk*dx)

    for i in range(0,nk):
        for j in range(0,nf):
            if k[i] == 0.:
                H[i,j] = 1
            else: 
                velocity = (f[j]/k[i])*1e-3    
                if velocity >= vmin and velocity <= vmax:
                    H[i,j] = 0
                else:
                    H[i,j] = 1

    t = 1 - np.abs(np.linspace(-1, 1, spread))
    kernel = t.reshape(spread, 1) * t.reshape(1, spread)
    H = scipy.signal.convolve2d(H, kernel, mode='same') #smooth edges of filter

    # show filter
    plt.imshow(H,extent=[-1/(2*dx),1/(2*dx),-1e-6/(2*dt),1e-6/(2*dt)],aspect='auto',cmap = 'gray')
    plt.colorbar()
    plt.ylim((0,1e-6/(2*dt)))
    plt.ylabel('Frequency (MHz)')
    plt.xlabel('Spatial Frequency (1/mm)')
    plt.show()

    # apply filter to data
    F = stream_fft*H 
    
    # convert back to time domain
    F_ifft = fft.ifft2(fft.fftshift(F))
    filtered_data = np.rot90(F_ifft[0:nx,0:nt],1)

    # show filtered data
    plt.imshow(filtered_data.real,extent=[stream[0].stats.position,stream[len(stream)-1].stats.position,0,stream[0].stats.npts*stream[0].stats.delta*1e6],aspect='auto',cmap = colormap)
    ax.autoscale(False)
    plt.gca().invert_yaxis()
    cbar = plt.colorbar()
    if stream[0].stats.calib_unit.rstrip() == 'nm/V':
        cbar.set_label('Displacement (nm)')
    elif stream[0].stats.calib_unit.rstrip() == 'mm/s/V':
        cbar.set_label('Particle Velocity (mm/s)')
    plt.ylabel('Time ($\mu$s)')
    plt.xlabel('Scan Location ('+stream[0].stats.position_unit+')')
    plt.show()

def picker(event):
    ''' 
    Generic picker for selecting points in a figure.  
    Left-click selects point and plots to figure. 
    Right-click removes point and deletes from figure.
    Returns: 
        px : array of final selected x values.
        py : array of final selected y values.
    '''

    tb = plt.get_current_fig_manager().toolbar 
    if tb.mode == '' and event.inaxes: # checks that toolbar is not in use (e.g. zoom)
        if event.button == 1: # left-click selects point
            px.append(event.xdata)
            py.append(event.ydata)
            ax.plot(event.xdata,event.ydata,'x',color='red')
            plt.show() 
        elif event.button == 3: # right-click removes point
            del px[len(px)-1]
            del py[len(py)-1]
            del ax.lines[len(ax.lines)-1] 
            plt.show()
    return px,py

def pickV(event):
    ''' 
    Picker for selecting points in fk plots.  When selected, the cooresponding velocity is displayed.  
    Left-click selects point and plots to figure. 
    Right-click removes point and deletes from figure.
    Returns: 
        px : array of final selected x values (frequency).
        py : array of final selected y values (wavenumber).
    Returns arrays px and py, the (final) selected x and y values, respectively.
    '''

    tb = plt.get_current_fig_manager().toolbar 
    annotations = []
    if tb.mode == '' and event.inaxes: # checks that toolbar is not in use (e.g. zoom)
        if event.button == 1: # left-click selects point and displays velocity
            px.append(event.xdata)
            py.append(event.ydata)
            ax.plot(event.xdata,event.ydata,'x',color='red')
            v = event.xdata/event.ydata*1e3
            annotations.append(ax.annotate(str(int(v))+'m/s',xy=(event.xdata,event.ydata),xytext=None))
            plt.show() 
        elif event.button == 3: # right-click removes point and displays velocity
            del px[len(px)-1]
            del py[len(py)-1]
            del ax.lines[len(ax.lines)-1] 
            del ax.texts[len(annotations)-1]
            plt.show()
    return px,py

def submitV(event): # 'enter' submits velocity points
    '''  
    Closes fk spectrum plot for fkfilter() and prints chosen velocity values when 'enter' is pressed on the keyboard and exactly 2 points are selected.
    '''

    if event.key == 'enter':
        if len(px) > 2:
            print 'Too many points chosen, choose only two velocity values'
        elif len(px) < 2:
            print 'Choose more points! At least two velocity points are needed'
        else:
            for i in range(len(px)):
                print 'velocity ' + str(i+1) + ': ' + str(int((px[i]/py[i])*1e3)) + ' m/s'
                plt.close()
    
    
