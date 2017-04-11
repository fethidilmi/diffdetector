'''
by: Arash Molavi Kakhki (arash.molavi@gmail.com) -- Nov 2016 -- ALL RIGHTS RESERVED

Say you've done a bunch of pcaps in a folder (e.g. from Netflix streams). You need to run this:

    pythin plotXputs.py [path to folder containing pcaps]
    
This will plot timeseries plots of throughputs for all pcaps in that folder.
'''

import sys, subprocess, os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

try:
    import seaborn as sns; sns.set()
except ImportError:
    pass

def parseTsharkXputOutput(output):
    '''
    ************ WORKS WITH tshark 1.12.1 ONLY ************
    
    Takes the output of tshark xput command, i.e. tshark -qz io,stat,interval 
    and parses the results into an ordered list 
    '''
    lines       = output.splitlines()
    end         = lines[4].partition('Duration:')[2].partition('secs')[0].replace(' ', '')
    lines[-2]   = lines[-2].replace('Dur', end)
    
    x = []
    y = []
    
    for l in lines:
        if '<>' not in l:
            continue
        
        l      = l.replace('|', '')
        l      = l.replace('<>', '')
        parsed = map(float, l.split())
        end   = float(parsed[1])
        start = float(parsed[0])
        dur   = float(end - start)
        
        if dur == 0:
            continue
        
        xput = float(parsed[-1])/dur
        
        y.append(xput)
        x.append(end)
    
    #converting to Mbits/sec
    y = map(lambda x: x*8/1000000.0, y)
    
    return x, y

def doOne(pcapFile, color='r', title=False):
    xputInterval = 0.25
    cmd          = ['tshark', '-r', pcapFile, '-qz', 'io,stat,{}'.format(xputInterval)]
    p            = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, err  = p.communicate()
    x, y         = parseTsharkXputOutput(output)
    
    plt.plot(x, y, color, label='')
    plt.legend()
    plt.grid()
    plt.xlabel('time (s)')
    plt.ylabel('Xput (Mbps)')
    if title:
        plt.title(title)
    plt.savefig('{}.png'.format(pcapFile))
    # plt.clf()

def main():
    colors = ['r', 'b', 'g', 'b', 'k']
    fileORfolders = sys.argv[1:]
    
    for fileORfolder in fileORfolders:
        fileORfolder = os.path.abspath(fileORfolder)
        if fileORfolder.endswith('/'):
            fileORfolder = fileORfolder[:-1]
        title = fileORfolder.rpartition('/')[2]
    	if os.path.isdir(fileORfolder):
            	print 'Doing:', fileORfolder
    		pcapFiles = filter(lambda x: x.endswith('.pcap'), os.listdir(fileORfolder))
    		i = 0
	        for pcapFile in pcapFiles:
	        	print '\tDoing:', pcapFile
    	    		doOne(fileORfolder + '/' + pcapFile, color=colors[i%len(colors)], title=title)
                    	i += 1
		plt.clf()

    	if os.path.isfile(fileORfolder):
    		for pcapFile in fileORfolder:
			    print 'Doing2:', pcapFile
    	    	doOne(pcapFile)
    	    	plt.clf()

if __name__=="__main__":
    main()