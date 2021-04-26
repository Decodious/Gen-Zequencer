from microbit import *
import random
import microbit

#GlobalVar
size = 8
bpm = 128
array = []
step = 0

#GlobalArr
neighbourpos = [[-1, 0], [-1, 1], [0, 1], [1, 1], [1, 0], [1, -1], [0, -1], [-1, -1]] #allows cell to look for neighbours
viewneighbourpos = [[0, 0], [0, +1], [+1, 0], [+1, +1]] #allows display LED to look for neighbours
note = [0, 1, 2, 3, 4, 5, 6, 7] #output MIDI values

#MIDI Functions
def startMIDI():
    uart.init(baudrate=31250, bits=8, parity=None, stop=1, tx=pin0) #starts the MIDI protocol

def midiNoteOn(chan, n, vel):
    MIDI_NOTE_ON = 0x90
    if chan > 15:
        return
    if n > 127:
        return
    if vel > 127:
        return
    msg = bytes([MIDI_NOTE_ON | chan, n, vel])
    uart.write(msg) #defines how to send a MIDI Note On message

def midiNoteOff(chan, n, vel):
    MIDI_NOTE_OFF = 0x80
    if chan > 15:
        return
    if n > 127:
        return
    if vel > 127:
        return
    msg = bytes([MIDI_NOTE_OFF | chan, n, vel])
    uart.write(msg) #defines how to send a MIDI Note Off message

#array Functions
def startarray(size):
    content = []
    for j in range(size):
        for i in range(size): #nested for loop to allow for matrix like operation
            content.append(random.randint(0, 1)) #creates 8 random numbers in a list
        array.append(content) #adds this list to another as an entry 8 times
        content = [] #clear content for next 8 random values
    return(array) #returns array of 8x8 on or off values

def itter(size, array, neighbourpos):
    nextarray = [] #this nextarray only exists inside the itter function
    for i in range(size):
        for j in range(size): #nested for loop to allow for matrix like operation
            neighbours = 0 #def neighbours and resets count
            for x in neighbourpos: #dealing with boundaries looking if it is looking out of range
                pointx = i + x[0]
                if pointx == -1:
                    pointx = size-1
                if pointx == size:
                    pointx -= size
                pointy = j + x[1]
                if pointy == -1:
                    pointy = size-1
                if pointy == size:
                    pointy -= size
                neighbour = array[pointx][pointy] # searches for values of 1 in the array acording to neighbourpos array
                if neighbour == 1: #if it finds a neighbour then add one to the neighbours count
                    neighbours += 1
            nextval = 0 #define default of 0 for next cell value
            if array[i][j] == 1: #if a cell is alive apply these rules:
                if neighbours < 2 or neighbours > 3:
                    nextval = 0
                elif neighbours == 2 or neighbours == 3:
                    nextval = 1
            if neighbours == 3: #if a cell is dead apply this rule:
                nextval = 1
            nextarray.append(nextval) #nextarray is then given all 64 values
    array = [] #original array is cleared for memory
    for i in range(size):
        content = nextarray[(size*i):(size*(i+1))] #take 8 values and put it inside content to be appended to array
        array.append(content) #appending a list makes it an 8x8 list instead of 1x64
    content = []
    return(array) #returns the new array

#Display Functions
def display(array, size, viewneighbourpos):
    nextarray = [] #this nextarray only exists inside the display function
    viewarray = [] #defines the array which the display will read from
    for i in range(0, size, 2): #searches in steps of 2, meaning a 2x2 grid is formed.
        for j in range(0, size, 2):
            neighbours = 0
            for x in viewneighbourpos: #searches using viewneighbourpos array
                pointx = i + x[0]
                pointy = j + x[1]
                neighbour = array[pointx][pointy]
                if neighbour == 1:
                    neighbours = neighbours + 1
            nextarray.append(neighbours)
    for i in range(4):
        content = nextarray[(4*i):(4*(i+1))] #create a 4x4 grid oppose to a 1x16
        viewarray.append(content)
    content = []
    for i in range(4):
        for j in range(4):
            microbit.display.set_pixel(j, i, (viewarray[j][i]*2)) #set pixels to this view array

def metro(step): #create lights which show how far along in the sequence the play head is
    microbit.display.set_pixel(0, 4, 0)
    microbit.display.set_pixel(1, 4, 0)
    microbit.display.set_pixel(2, 4, 0)
    microbit.display.set_pixel(3, 4, 0)
    if step == 1:
        microbit.display.set_pixel(0, 4, 9)
    elif step == 2:
        microbit.display.set_pixel(0, 4, 5)
    elif step == 3:
        microbit.display.set_pixel(1, 4, 9)
    elif step == 4:
        microbit.display.set_pixel(1, 4, 5)
    elif step == 5:
        microbit.display.set_pixel(2, 4, 9)
    elif step == 6:
        microbit.display.set_pixel(2, 4, 5)
    elif step == 7:
        microbit.display.set_pixel(3, 4, 9)
    elif step == 8:
        microbit.display.set_pixel(3, 4, 5)

#Play Functions
def nextstep(step, size): #simple tracker to conduct the rest of the code
    step += 1
    if step == size + 1:
        step = 1
    return(step)

def notesOn(size, step, note): #simple note on function
    for i in range(size):
        if array[step - 1][i] == 1:
            midiNoteOn(0, note[i], 64)

def notesOff(size, step, note):
    for i in range(size): #simple note off function
        if array[step - 1][i] == 1:
            midiNoteOff(0, note[i], 64)

#Start Up - Runs once when the device starts up
startarray(size)
display(array, size, viewneighbourpos)
metro(step)
startMIDI()

#Interaction - Constantly running
while True:
    if microbit.button_a.is_pressed():
        playstate = 1
        while playstate == 1:
            step = nextstep(step, size) #update all functions with 'step'
            metro(step)
            notesOn(size, step, note)
            sleep(60/bpm*1000)
            notesOff(size, step, note)
            if microbit.button_b.is_pressed(): #after notes are played check if B is pressed for a reset
                array = []
                startarray(size)
                display(array, size, viewneighbourpos)
            sleep(60/bpm*1000)
            if microbit.button_a.is_pressed(): #after notes are played check if A is pressed for a stop
                step = 0
                metro(step)
                sleep(1000)
                break
            if step == 8: #when step == 8 then itterate the array allowing for new sounds to be made
                array = itter(size, array, neighbourpos)
                display(array, size, viewneighbourpos)
    if microbit.button_b.is_pressed(): #if the array isn't playing and you want a new seed to start from press B
        array = []
        startarray(size)
        display(array, size, viewneighbourpos)
        sleep(500)