import sys
import json
import os

from PyQt6.QtWidgets import *
from PyQt6.QtCore import QTimer, QTime
from PyQt6.QtGui import QFont

class TimerApp(QWidget):
    def __init__(self):
        super().__init__()

        self.timer = QTimer()
        self.time_left = QTime(0, 0)
        self.config_file = 'config.json'
        self.last_file = ''
        
        self.radio_group = QButtonGroup(self)
        self.radio_to_offset = {}
        self.headers_added = False

        self.last_set_time = QTime(0, 0)

        self.init_ui()
        self.load_last_file()
        self.apply_theme_from_file("theme.css")

    def init_ui(self):
        self.setWindowTitle("Python FlowTimer ~ obby")
        self.resize(1079, 338)

        self.main_layout = QVBoxLayout()

        self.timer_h_layout = QHBoxLayout()
        self.timer_h_layout.addStretch(1)  # Adds a stretch on the left side
        self.label = QLabel('00:00', self)
        self.label.setFont(QFont('Arial', 72))  # Increase the font size
        self.timer_h_layout.addWidget(self.label)  # Adds the label to the horizontal layout
        self.timer_h_layout.addStretch(1)  
        
        self.label.setObjectName("timerLabel")
        
        self.main_layout.addStretch(1)  # Adds a stretch above the label layout
        self.main_layout.addLayout(self.timer_h_layout)  # Adds the horizontal layout of the label to the main layout
        self.main_layout.addStretch(1)  # Adds a stretch below the label layout

        self.mid_layout = QHBoxLayout()
        self.button_layout = QVBoxLayout()

        self.add_button = QPushButton('Add', self)
        self.add_button.setFixedSize(121, 25)
        self.add_button.clicked.connect(self.add_timer_row)
        self.button_layout.addWidget(self.add_button)

        self.start_button = QPushButton('Start', self)
        self.start_button.setFixedWidth(121)
        self.start_button.setFixedHeight(25)
        self.start_button.clicked.connect(self.start_timer)
        self.button_layout.addWidget(self.start_button)

        self.stop_button = QPushButton('Stop', self)
        self.stop_button.setFixedWidth(121)
        self.stop_button.setFixedHeight(25)
        self.stop_button.clicked.connect(self.stop_timer)
        self.button_layout.addWidget(self.stop_button)

        self.settings_button = QPushButton('Settings', self)
        self.settings_button.setFixedWidth(121)
        self.settings_button.setFixedHeight(25)
        self.button_layout.addWidget(self.settings_button)

        self.load_button = QPushButton('Load Timers', self)
        self.load_button.setFixedWidth(121)
        self.load_button.setFixedHeight(25)
        self.load_button.clicked.connect(self.load_timers)
        self.button_layout.addWidget(self.load_button)

        self.save_button = QPushButton('Save Timers', self)
        self.save_button.setFixedWidth(121)
        self.save_button.setFixedHeight(25)
        self.save_button.clicked.connect(self.save_timers)
        self.button_layout.addWidget(self.save_button)

        self.mid_layout.addLayout(self.button_layout)
        self.timer_rows_layout = QVBoxLayout()
        self.mid_layout.addLayout(self.timer_rows_layout)
        
        self.main_layout.addLayout(self.mid_layout)

        self.setLayout(self.main_layout)

        self.timer.timeout.connect(self.update_timer)
        
        self.add_timer_row()
        self.add_header_row()
        
    def add_timer_row(self, name='', offsets='', interval='', beeps=''):
        # If header labels haven't been added yet
        if not self.headers_added:
            self.add_header_labels()
            self.headers_added = True

        row_layout = QHBoxLayout()

        radio_button = QRadioButton(self)
        radio_button.toggled.connect(self.radio_button_toggled)
        
        name_edit = QLineEdit(self)
        name_edit.setPlaceholderText("Name")
        if name != False:
            name_edit.setText(str(name))
        
        offset_edit = QLineEdit(self)
        offset_edit.setPlaceholderText("Offsets")
        offset_edit.setText(offsets)
        
        self.radio_group.addButton(radio_button)
        self.radio_to_offset[radio_button] = offset_edit
        radio_button.toggled.connect(self.radio_button_toggled)

        interval_edit = QLineEdit(self)
        interval_edit.setPlaceholderText("Interval")
        interval_edit.setText(interval)
        
        beeps_edit = QLineEdit(self)
        beeps_edit.setPlaceholderText("Beeps")
        beeps_edit.setText(beeps)
        
        delete_button = QPushButton('Delete', self)
        delete_button.setFixedSize(121, 25)
        delete_button.clicked.connect(lambda: self.delete_timer_row(row_layout))

        row_layout.addWidget(radio_button)
        row_layout.addWidget(name_edit)
        row_layout.addWidget(offset_edit)
        row_layout.addWidget(interval_edit)
        row_layout.addWidget(beeps_edit)
        row_layout.addWidget(delete_button)

        self.timer_rows_layout.addLayout(row_layout)

    def add_header_labels(self):
        header_layout = QHBoxLayout()

        header_layout.addWidget(QLabel(""))  # For the radio button
        header_layout.addWidget(QLabel("Name"))
        header_layout.addWidget(QLabel("Offsets"))
        header_layout.addWidget(QLabel("Interval"))
        header_layout.addWidget(QLabel("Beeps"))
        header_layout.addWidget(QLabel(""))  # For the delete button

        self.timer_rows_layout.addLayout(header_layout)
        
    def delete_timer_row(self, row_layout):
        if row_layout == self.timer_rows_layout.itemAt(0):
            return
        # Remove widgets from row_layout
        for i in reversed(range(row_layout.count())):
            widget = row_layout.itemAt(i).widget()
            if widget:
                widget.close()

        # Remove the layout from the main layout
        self.timer_rows_layout.removeItem(row_layout)

        # Clean up the radio button references
        for radio_button in self.radio_to_offset.keys():
            if self.radio_to_offset[radio_button].parent() is None:  # If the widget has been deleted
                del self.radio_to_offset[radio_button]
                break

    def toggle_advanced_settings(self, checked):
        self.name_edit.setVisible(checked)
        self.offset_edit.setVisible(checked)
        self.interval_edit.setVisible(checked)
        self.beeps_edit.setVisible(checked)

    def set_timer(self):
        time, _ = QTimeEdit.get_time(self, "Set Timer")
        if time:
            self.time_left = time
            self.label.setText(time.toString())

    def update_timer(self):
        self.time_left = self.time_left.addMSecs(-1)  # Subtract 1000 milliseconds (1 second)
        hours = self.time_left.hour()
        minutes = self.time_left.minute()
        seconds = self.time_left.second()
        milliseconds = self.time_left.msec()

        if hours == 0 and minutes < 60:
            formatted_time = f"{minutes * 60 + seconds}.{milliseconds:03d}"
        else:
            formatted_time = self.time_left.toString("hh:mm:ss")
        
        self.label.setText(formatted_time)
        
        if self.time_left == QTime(0, 0):
            self.timer.stop()


    def start_timer(self):
        # Check if the timer is currently active
        if self.timer.isActive():
            self.timer.stop()  # Stop the timer
            self.time_left = self.last_set_time  # Reset to the last set time

            # Update the label with the reset time
            hours = self.time_left.hour()
            minutes = self.time_left.minute()
            seconds = self.time_left.second()
            milliseconds = self.time_left.msec()

            if hours == 0 and minutes < 60:
                formatted_time = f"{minutes * 60 + seconds}.{milliseconds:03d}"
            else:
                formatted_time = self.time_left.toString("hh:mm:ss")

            self.label.setText(formatted_time)
            self.timer.start(1)

        elif self.time_left > QTime(0, 0):
            print("Starting timer with time:", self.time_left.toString("hh:mm:ss.zzz"))
            self.timer.start(1)
        else:
            print("INVALID TIME")



    def stop_timer(self):
        self.timer.stop()
        self.time_left = self.last_set_time

        hours = self.time_left.hour()
        minutes = self.time_left.minute()
        seconds = self.time_left.second()
        milliseconds = self.time_left.msec()

        if hours == 0 and minutes < 60:
            formatted_time = f"{minutes * 60 + seconds}.{milliseconds:03d}"
        else:
            formatted_time = self.time_left.toString("hh:mm:ss")

        self.label.setText(formatted_time)

    def load_timers(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Load Timers", "", "JSON Files (*.json);;All Files (*)")
        if file_name:
            self.load_timers_from_file(file_name)
            self.save_last_file(file_name)

    def load_timers_from_file(self, file_name):
        with open(file_name, 'r') as file:
            data = json.load(file)
            # Corrected way to clear a layout
            self.clear_layout(self.timer_rows_layout)
            # End of correction
            for timer in data['Timers']:
                self.add_timer_row(name=timer['Name'], offsets=timer['Offsets'], interval=timer['Interval'], beeps=timer['NumBeeps'])

    def save_timers(self):
        timers = []
        for i in range(self.timer_rows_layout.count()):
            layout = self.timer_rows_layout.itemAt(i)
            name = layout.itemAt(1).widget().text()
            offsets = layout.itemAt(2).widget().text()
            interval = layout.itemAt(3).widget().text()
            beeps = layout.itemAt(4).widget().text()
            if name or offsets or interval or beeps:  # To prevent saving empty rows
                timers.append({'Name': name, 'Offsets': offsets, 'Interval': interval, 'NumBeeps': beeps})

        file_name, _ = QFileDialog.getSaveFileName(self, "Save Timers", "", "JSON Files (*.json);;All Files (*)")
        if file_name:
            with open(file_name, 'w') as file:
                json.dump({'Header': {'Version': 48}, 'Timers': timers}, file)
            self.save_last_file(file_name)

    def save_last_file(self, file_name):
        with open(self.config_file, 'w') as config:
            json.dump({'last_file': file_name}, config)

    def load_last_file(self):
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r') as config:
                data = json.load(config)
                self.last_file = data.get('last_file', '')
                if os.path.exists(self.last_file):
                    self.load_timers_from_file(self.last_file)
                else:
                    self.add_timer_row()
        else:
            self.add_timer_row()
            
    def clear_layout(self, layout):
        for i in reversed(range(layout.count())):
            item = layout.takeAt(i)
            if isinstance(item, QWidgetItem):
                item.widget().close()  # if it's a widget, close it
            elif isinstance(item, QLayout):
                self.clear_layout(item)  # if it's another layout, recursively clear it
            layout.removeItem(item)  # finally, remove the item from layout
    
    def update_timer_from_offsets(self, offset_edit_widget):
        offsets = offset_edit_widget.text()
        try:
            # Parse the string to get the last number.
            last_offset = int(offsets.split("/")[-1])
            
            # Convert the last number to minutes, seconds, and milliseconds.
            minutes = last_offset // 60000
            remainder = last_offset % 60000
            seconds = remainder // 1000
            milliseconds = remainder % 1000
            
            # Update self.time_left and also store it as the last set time
            self.time_left = QTime(0, minutes, seconds, milliseconds)
            self.last_set_time = self.time_left
            
            formatted_time = f"{minutes * 60 + seconds}.{milliseconds:03d}"  # Format milliseconds with zero-padding
            self.label.setText(formatted_time)
        except Exception as e:
            print("Error updating timer:", e)


            
    def radio_button_toggled(self, checked):
        if checked:  # Only execute when a radio button is checked (turned on)
            self.timer.stop()
            radio_button = self.sender()
            offset_edit = self.radio_to_offset.get(radio_button)
            if offset_edit:
                print("Updating timer from offset:", offset_edit.text())  # Debug print
                self.update_timer_from_offsets(offset_edit)

    def apply_theme_from_file(self, filename):
        """Apply styles from a given CSS file."""
        with open(filename, 'r') as theme_file:
            self.setStyleSheet(theme_file.read())

    def add_header_row(self):
        header_layout = QHBoxLayout()

        # Use a QLabel with an empty text for radio button placeholder
        header_layout.addWidget(QLabel('', self))
        
        name_header = QLabel('Name', self)
        offset_header = QLabel('Offsets', self)
        interval_header = QLabel('Interval', self)
        beeps_header = QLabel('Beeps', self)
        
        header_layout.addWidget(name_header)
        header_layout.addWidget(offset_header)
        header_layout.addWidget(interval_header)
        header_layout.addWidget(beeps_header)
        header_layout.addWidget(QLabel('', self))  # Placeholder for the delete button

        self.timer_rows_layout.addLayout(header_layout)


app = QApplication(sys.argv)
window = TimerApp()
window.show()
sys.exit(app.exec())
