from picamera import PiCamera
from time import sleep
import Adafruit_DHT
from tkinter import *
from PIL import Image
from PIL import ImageTk
import math
import csv
import datetime
import time
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator
import plotly 
import plotly.plotly as py
import plotly.graph_objs as go
import plotly.figure_factory as FF
import matplotlib.dates as mdates
import numpy as np
import pandas as pd
import schedule
from pandas.plotting import register_matplotlib_converters


class MainGUI:
    def __init__(self):
        #self.window = window
        register_matplotlib_converters()
        window = Tk()
        window.title("AutoKit V1.1")
        
        menu_bar = Menu(window)
        file_menu = Menu(menu_bar, tearoff=0)
        file_menu.add_command(label="Exit", command=window.destroy)
        menu_bar.add_cascade(label="File", menu=file_menu)
        window.config(menu=menu_bar)

        #mainF = LabelFrame(window)
        #mainF.grid(row=1,column=1)
        
        infoFrame = LabelFrame(window, bd=5)
        infoFrame.grid(row=1, column=1)
        
        name_var1 = "Sour Banana Sherbert x Puta Breath"
        date_var1 = "June 19, 2019"
        date_var_begin = datetime.datetime.strptime("2019, 06, 19" , "%Y, %m, %d")
        now = datetime.datetime.now()
        #now = now.strftime("%Y, %m, %d")
        x, y, z = now.year, now.month, now.day
        
        #date_var_now = datetime.datetime.strptime(datenow, "%Y, %m, %d")
        day_count = (now - date_var_begin)
        day_count = day_count.days
        print(day_count)
        
        
        
        #pLabel = Label(infoFrame, text = "Project Name: " + name_var1).grid(row=1, column=1)
        #sLabel = Label(infoFrame, text = "Project Start Date: " + date_var1).grid(row=2, column=1)
        #dLabel = Label(infoFrame, text = "Project Day Counter:").grid(row=3, column=1, sticky=E)

        self.camera = PiCamera()
        self.current_pic = self.takePicture()
        self.current_pic=Image.open(self.current_pic)
        self.current_pic=self.current_pic.resize((500, 330), Image.ANTIALIAS)
        self.current_image= ImageTk.PhotoImage(self.current_pic)
        
        #pic_Frame=Frame(infoFrame)
        #pic_Frame.grid(row=3, column=1)
        
        self.current_image_label = Label(infoFrame, image=self.current_image)
        self.current_image_label.configure(image=self.current_image)
        self.current_image_label.image=self.current_image
        self.current_image_label.grid(row=3, column=1, padx=10, pady=(5,0))
        
        pic_button_Frame=Frame(infoFrame)
        pic_button_Frame.grid(row=4, column=1, sticky='nw', padx=10)
        
        self.refresh_pic = Button(pic_button_Frame, text="Refresh photo", command=self.timelapsePicture)
        self.refresh_pic.grid(row=1, column=1, sticky='nw')
        
        self.play_timelapse = Button(pic_button_Frame, text="Play timelapse")
        self.play_timelapse.grid(row=1, column=2, sticky='nw')
        
        
        
        currents_Frame = LabelFrame(infoFrame, text = "Currents", width=20)
        currents_Frame.grid(row=3, column=2)
        
        humidity, temperature_F, vapor_pressure_deficit = self.recTempAndHumidity()
        
        #dg=u"{DEGREE SIGN}"
        self.dg=('\u00B0')
        temperature_F=("\n{:.1f}".format(temperature_F)+self.dg+"F\n")
        self.t_label = Label(currents_Frame, text=temperature_F, font=48)
        self.t_label.grid(row=1, column = 1)
        
        humidity=("\n{:.1f}%RH \n".format(humidity))
        self.h_label = Label(currents_Frame, text=humidity, font=48)
        self.h_label.grid(row=2, column = 1)
        
        vapor_pressure_deficit = ("\n{:.2f} hPa\n".format(vapor_pressure_deficit))
        self.v_label = Label(currents_Frame, text=vapor_pressure_deficit, font=48)
        self.v_label.grid(row=3, column = 1)
        
        #days_Frame=Label(currents_Frame)
        #days_Frame.grid(row=4, column=1)
        #day_count.Text = day_count.ToString()
        day_counter=Label(currents_Frame, text = day_count, font=48)
        day_counter.grid(row=4, column=1)
        days_label=Label(currents_Frame, text="Days")
        days_label.grid(row=5, column=1)
        
        self.chart_pic = self.updateTempHumChart()
        #self.chart_pic=('/home/pi/Desktop/image.jpg')
        self.chart_pic = Image.open(self.chart_pic)
        self.chart_pic=self.chart_pic.resize((500, 330), Image.ANTIALIAS)
        self.chartimg= ImageTk.PhotoImage(self.chart_pic)
        
        self.chart_label = Label(infoFrame, image=self.chartimg)
        self.chart_label.image=self.chartimg
        self.chart_label.grid(row=3, column = 3, columnspan=2, padx=10, pady=(5,0))
        
        chart_button_Frame=Frame(infoFrame)
        chart_button_Frame.grid(row=4, column=3, sticky='nw', padx=10)
        
        self.show_last = Button(chart_button_Frame, text="Show last:")
        self.show_last.grid(row=1, column=1, sticky='nw')
        
        self.eight_hr_chart = Button(chart_button_Frame, text="8hrs")
        self.eight_hr_chart.grid(row=1, column=2, sticky='nw')
        
        self.two_day_chart = Button(chart_button_Frame, text="2days")
        self.two_day_chart.grid(row=1, column=3, sticky='nw')
        
        self.one_week_chart = Button(chart_button_Frame, text="week")
        self.one_week_chart.grid(row=1, column=4, sticky='nw')
        
        
        
        notes_Frame = LabelFrame(infoFrame, text="Notes")
        notes_Frame.grid(row=5, column=1, sticky='w', padx=10)
        self.notes_box = Text(notes_Frame, width=18, height=10, wrap='word')
        self.notes_box.grid()
        previous_notes= open ('/home/pi/GrowBox/NotesBox.txt', 'r')
        previous_notes = previous_notes.read()
        self.notes_box.insert(END, previous_notes)
        
        #previous_notes.close()
        
        deviceStatus_Frame = LabelFrame(infoFrame, bd=10, text="Device Status")
        deviceStatus_Frame.grid(row=5, column=1, columnspan=2, sticky='e', pady=10)
       
        
        self.t_btn1 = Button(deviceStatus_Frame, bd=10, text="LIGHTS OFF", width=12, command = lambda:[ \
               self.t_btn1.config(text="LIGHTS ON") \
               if self.t_btn1.config('text')[-1] == 'LIGHTS OFF'\
               else self.t_btn1.config(text="LIGHTS OFF")])
        self.t_btn1.grid(row=1, column=1)
        
        self.t_btn2 = Button(deviceStatus_Frame, bd=10, text="FANS OFF", width=12, command = lambda:[ \
            self.t_btn2.config(text="FANS ON") \
            if self.t_btn2.config('text')[-1] == 'FANS OFF'\
            else self.t_btn2.config(text="FANS OFF")])
        self.t_btn2.grid(row=2, column=1)
        
        self.t_btn3 = Button(deviceStatus_Frame, bd=10, text="HUMIDIFIER OFF", width=12, command = lambda:[ \
            self.t_btn3.config(text="HUMIDIFIER ON") \
            if self.t_btn3.config('text')[-1] == 'HUMIDIFIER OFF'\
            else self.t_btn3.config(text="HUMIDIFIER OFF")])
        self.t_btn3.grid(row=3, column=1)
        
        self.t_btn4 = Button(deviceStatus_Frame, bd=10, text="FAN 2 OFF", width=12, command = lambda:[ \
            self.t_btn4.config(text="FAN 2 ON") \
            if self.t_btn4.config('text')[-1] == 'FAN 2 OFF'\
            else self.t_btn4.config(text="FAN 2 OFF")])
        self.t_btn4.grid(row=1, column=2)
        
        self.t_btn5 = Button(deviceStatus_Frame, bd=10, text="DEHUMIDIFIER OFF", width=12, command = lambda:[ \
            self.t_btn5.config(text="DEHUMIDIFIER ON") \
            if self.t_btn5.config('text')[-1] == 'HUMIDIFIER OFF'\
            else self.t_btn5.config(text="HUMIDIFIER OFF")])
        self.t_btn5.grid(row=2, column=2)
        
        self.t_btn6 = Button(deviceStatus_Frame, bd=10, text="HEATER OFF", width=12, command = lambda:[\
            self.t_btn6.config(text="HEATER ON")\
            if self.t_btn6.config('text')[-1] == 'HEATER OFF'\
            else self.t_btn6.config(text="HEATER OFF")])
        self.t_btn6.grid(row=3, column=2)
        
        self.t_btn7 = Button(deviceStatus_Frame, bd=10, text="AIR FILTER OFF", width=12, command = lambda:[\
            self.t_btn7.config(text="AIR FILTER ON")\
            if self.t_btn7.config('text')[-1] == 'AIR FILTER OFF'\
            else self.t_btn7.config(text="AIR FILTER OFF")])
        self.t_btn7.grid(row=1, column=3)
        
        self.t_btn8 = Button(deviceStatus_Frame, bd=10, text="AIR COND OFF", width=12, command = lambda:[ \
            self.t_btn8.config(text="AIR COND ON") \
            if self.t_btn8.config('text')[-1] == 'AIR COND OFF'\
            else self.t_btn8.config(text="AIR COND OFF")])
        self.t_btn8.grid(row=2, column=3)
        
        self.t_btn9 = Button(deviceStatus_Frame, bd=10, text="TIMELAPSE OFF", width=12, command = lambda:[ \
            self.t_btn9.config(text="TIMELAPSE ON") \
            if self.t_btn9.config('text')[-1] == 'TIMELAPSE OFF'\
            else self.t_btn9.config(text="TIMELAPSE OFF")])
        self.t_btn9.grid(row=3, column=3)
        
        automation_Frame = LabelFrame(infoFrame, text = "Automation")
        automation_Frame.grid(row=5, column=3, columnspan=2, padx=10, pady=10, sticky='we')
        
        self.apply_changes_button = Button(automation_Frame, text = "Apply All")
        self.apply_changes_button.grid(row=5, column = 3, padx=10, pady=10)
        
        #self.lock_btn = Checkbutton(automation_Frame, text="Lock", fontsize='10')
        #self.lock_btn.grid(row=1, column=5)
        
        lights_Frame = Frame(automation_Frame)
        lights_Frame.grid(row=2, column=3, padx=10)
        
        self.hour_var1 = StringVar(window)
        self.hour_var2 = StringVar(window)
        
        self.hour_list=["06:00", "12:00","22:00"]
        self.lights_on_box = OptionMenu(lights_Frame, self.hour_var1, *self.hour_list)
        self.text_a1 = Label(lights_Frame, text = "Lights on at: ")
        self.text_a1.grid(row=1, column = 1)
        self.lights_on_box.grid(row=1, column=2)
        self.hour_var1.set(self.hour_list[0])
        self.hour_var2.set(self.hour_list[2])
        
        self.lights_off_box = OptionMenu(lights_Frame, self.hour_var2, *self.hour_list)
        self.text_a2 = Label(lights_Frame, text = "Lights off at: ")
        self.text_a2.grid(row=2, column = 1)
        self.lights_off_box.grid(row=2, column=2)
        
        water_Frame = Frame(lights_Frame)
        water_Frame.grid(row=3, column=1, columnspan=2, padx=10, pady=(10,5))
        
        self.text_w1 = Label(water_Frame, text = "Water ")
        self.text_w1.grid(row=3, column=1, sticky='e')
        self.water_gal_box = Spinbox(water_Frame, width=4, from_=1, to=32)
        self.water_gal_box.grid(row=3, column=2)
        self.text_w2 = Label(water_Frame, text = "Litres ")
        self.text_w2.grid(row=3, column=3, sticky='w')
        
        self.text_w3 = Label(water_Frame, text = "Every ")
        self.text_w3.grid(row=4, column=1, sticky='e')
        self.water_gal_box = Spinbox(water_Frame, width=4, from_=1, to=32)
        self.water_gal_box.grid(row=4, column=2, sticky='e')
        self.text_w4 = Label(water_Frame, text = "Days ")
        self.text_w4.grid(row=4, column=3, sticky='w')
        
        self.water_now_btn = Button(water_Frame, text = "Water Now", width=12)
        self.water_now_btn.grid(row=5, column=1, columnspan=3, pady=(5,0))
        
        #sliders_Frame = Frame(automation_Frame)
        #sliders_Frame.grid(row=2, column = 1, pady=10)
        
        temp_Frame = LabelFrame(automation_Frame, text="Temperature")
        temp_Frame.grid(row=2, column = 1, rowspan=5, padx=5, pady=5, sticky='s')
        
        self.temp_max_scale = Scale(temp_Frame, from_=90, to=32, length=130)
        self.temp_max_scale.grid(row=1, column=1)
        self.temp_max_scale.set(76)
        label_a1=Label(temp_Frame, text= "Day")
        label_a1.grid(row=2, column=1, sticky='e')
        
        self.temp_min_scale = Scale(temp_Frame, from_=90, to=32, length=130)
        self.temp_min_scale.grid(row=1, column=2, sticky='e', padx=5)
        self.temp_min_scale.set(68)
        label_a2=Label(temp_Frame, text= "Night")
        label_a2.grid(row=2, column=2, sticky='e')
        
        self.temp_hyst1_scale = Scale(temp_Frame, from_=10, to=1, length=130)
        self.temp_hyst1_scale.grid(row=1, column=3, padx=(0,5))
        self.temp_hyst1_scale.set(2)
        label_a3=Label(temp_Frame, text= "Hyst")
        label_a3.grid(row=2, column=3, sticky='e')
        
        
        hum_Frame = LabelFrame(automation_Frame, text="Humidity")
        hum_Frame.grid(row=2, column=2, rowspan=5, sticky='s', padx=5, pady=5)
        
        self.humidity_max_scale = Scale(hum_Frame, from_=99, to=2, length=130)
        self.humidity_max_scale.grid(row=1, column=1)
        self.humidity_max_scale.set(50)
        label_a4=Label(hum_Frame, text= "Day")
        label_a4.grid(row=2, column=1, sticky='e')
        
        self.humidity_min_scale = Scale(hum_Frame, from_=99, to=2, length=130)
        self.humidity_min_scale.set(65)
        self.humidity_min_scale.grid(row=1, column=2, padx=5)
        label_a5=Label(hum_Frame, text= "Night")
        label_a5.grid(row=2, column=2, sticky='e')
        
        self.hum_hyst2_scale = Scale(hum_Frame, from_=10, to=1,length=130)
        self.hum_hyst2_scale.grid(row=1, column=3, padx=(0,5))
        self.hum_hyst2_scale.set(2)
        label_a6=Label(hum_Frame, text= "Hyst")
        label_a6.grid(row=2, column=3, sticky='e')
        
        
    
    
    
    
        self.chart_label.after(50000, self.updateGUI)
        #self.current_image_label.after(700000, self.timelapsePicture)
        #schedule.every().day.at("06:00").do(self.timelapsePicture)
        #schedule.every(1).minute.do(self.timelapsePicture)
        self.timelapsePicture()

        ##self.current_pic_label.after(60000, self.takePicture) not used
        window.mainloop()
        
    def takePicture(self):
        #camera = PiCamera()
        #date = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
        Pic_Path = ('/home/pi/GrowBox/GrowPictures/currentPic.jpg')
        #Pic_Name = Pic_Path + date + '.jpg'
        self.camera.rotation=180
        self.camera.start_preview()
        sleep(10)
        self.camera.capture(Pic_Path)
        self.camera.stop_preview()
        return Pic_Path
    
    def updatePicture(self):
        self.current_pic = self.takePicture()
        self.current_pic=Image.open(self.current_pic)
        self.current_pic=self.current_pic.resize((500, 330), Image.ANTIALIAS)
        self.current_image= ImageTk.PhotoImage(self.current_pic)
        self.current_image_label.configure(image=self.current_image)
        self.current_image_label.image=self.current_image
        
    
    
    
    def recTempAndHumidity(self):
        with open('TempLog.txt', mode='a') as sensor_log:
            humidity, temperature = Adafruit_DHT.read_retry(Adafruit_DHT.AM2302, 4)
            if humidity > 100.0:
                time.sleep(2)
                humidity, temperature = Adafruit_DHT.read_retry(Adafruit_DHT.AM2302, 4)
                
            temperature_F = ((temperature * 9.0/5.0)+32.0)
            dateN = datetime.datetime.now()
            sensor_writer = csv.writer(sensor_log, delimiter=',')
            sensor_writer.writerow([dateN, '{:.1f}'.format(temperature_F), '{:.1f}'.format(humidity)])
            # get vpd below
            saturation_vapor_pressure = 0.6108 * math.exp(17.27 * temperature / (temperature + 237.3))
            actual_vapor_pressure = humidity / 100 * saturation_vapor_pressure
            vapor_pressure_deficit = (actual_vapor_pressure - saturation_vapor_pressure)
        return humidity, temperature_F, vapor_pressure_deficit
        
    
    def updateTempHumChart(self):
        tempLog = pd.read_csv("TempLog.txt", parse_dates = [0],  index_col=[0])
        tempLog = tempLog.tail(4000)
        
        fig, ax = plt.subplots(2, sharex = True)
        tempLog.columns = ['Temperature', 'Humidity']
        ax[0].plot(tempLog['Temperature'], 'r')
        ax[0].grid(True)
        ax[0].minorticks_on()
        ax[0].set_title("Temperature")
        ax[0].set_ylabel("Fahrenheit")
        #ax[0].set_ylim(60, 80)
        #plt.ylabel("Temp")
        ax[1].plot(tempLog['Humidity'])
        ax[1].set_title("Humidity")
        ax[1].minorticks_on()
        ax[1].set_ylabel("%RH")
        
        plt.xticks(rotation=45)
        fig.autofmt_xdate()
        ax[1].xaxis.set_major_formatter(mdates.DateFormatter("%b-%d %-I:%M %p"))
        plt.xlabel("")
        plt.grid()
        fig.tight_layout()
        fig.savefig('/home/pi/GrowBox/sensorGraph.jpg', bbox_inches="tight")
        chart = ( '/home/pi/GrowBox/sensorGraph.jpg')
        #fig.show()
        return chart
    

    def updateGUI(self):
        humidity, temperature, vapor_pressure_deficit = self.recTempAndHumidity()
        
        temperature =("\n{:.1f}".format(temperature)+self.dg+"F\n")
        self.t_label.configure(text=temperature, font=48)
        
        humidity =("\n{:.1f} %RH \n".format(humidity))
        self.h_label.configure(text=humidity, font=48)
        
        vapor_pressure_deficit =("\n{:.2f} hPa\n".format(vapor_pressure_deficit))
        self.v_label.configure(text=vapor_pressure_deficit, font=48)
        
        plt.close('all')
        chart=self.updateTempHumChart()
        chart = Image.open(chart)
        chart=chart.resize((500, 330), Image.ANTIALIAS)
        image= ImageTk.PhotoImage(chart)
        self.chart_label.configure(image=image)
        self.chart_label.image=image
        self.chart_label.after(60000, self.updateGUI)
        
    def timelapsePicture(self):
        date = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
        Pic_Path = ('/home/pi/GrowBox/GrowPictures/GrowTimeLapse/')
        Pic_Name = Pic_Path + date + '.jpg'
        #self.camera.rotation=-90
        self.camera.start_preview()
        sleep(5)
        self.camera.capture(Pic_Name)
        self.camera.stop_preview()
        #currentPic=self.takePicture()
        currentPic = Image.open(Pic_Name)
        currentPic.save('/home/pi/GrowBox/GrowPictures/currentPic.jpg')
        currentPic=currentPic.resize((500, 330), Image.ANTIALIAS)
        image= ImageTk.PhotoImage(currentPic)
        self.current_image_label.configure(image=image)
        self.current_image_label.image=image
        #schedule.every(240).minutes.do(self.timelapsePicture)
        #self.current_image_label.after(28800000, self.timelapsePicture)
        
        
    def toggle_color(self):
        if self.t_btn["text"]=='ON':
            self.t_btn.configure(bg="yellow")
        else:
            self.t_btn.configure(bg="gray")
        
    
    
        
MainGUI()