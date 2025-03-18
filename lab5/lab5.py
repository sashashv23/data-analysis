import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, Button, CheckButtons
from scipy.signal import firwin, lfilter

# Ініціалізація параметрів для гармонічної функції та шуму
init_amplitude = 1.0
init_frequency = 1.0
init_phase = 0.0
init_noise_mean = 0.0
init_noise_variance = 0.1
init_cutoff = 2.0
init_order = 101

# Часова вісь для генерування сигналів
t = np.linspace(0, 2 * np.pi, 1000)

# Поточний шум, який можна оновлювати, коли змінюються слайдери
current_noise = np.random.normal(init_noise_mean, np.sqrt(init_noise_variance), len(t))

# Функція для генерування гармонічного сигналу з шумом
def harmonic_with_noise(amplitude, frequency, phase, noise_mean, noise_variance, show_noise):
    global current_noise
    harmonic = amplitude * np.sin(frequency * t + phase)  
    if show_noise:
        return harmonic + current_noise 
    return harmonic  

# Функція для застосування фільтра Фірса
def fir_filter(data, cutoff, fs=1000, order=101):
    nyquist = 0.5 * fs  
    normal_cutoff = cutoff / nyquist  
    b = firwin(order, normal_cutoff) 
    y = lfilter(b, 1.0, data)  
    return y  

# Налаштування графіка
fig, ax = plt.subplots(figsize=(10, 6), facecolor='white')
plt.subplots_adjust(left=0.1, bottom=0.3)
ax.set_title("Harmonic Function with Noise", fontsize=16, fontweight='bold', color='#a55166')
ax.set_xlabel("Time", fontsize=12, color='#a55166')
ax.set_ylabel("Amplitude", fontsize=12, color='#a55166')
ax.grid(True, which='both', linestyle='--', linewidth=0.5, color='#e2b4c1')
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.spines['left'].set_color('#a55166')
ax.spines['bottom'].set_color('#a55166')
ax.set_facecolor('white')

# Створення графіків для зашумленого та відфільтрованого сигналу
line, = ax.plot(t, harmonic_with_noise(init_amplitude, init_frequency, init_phase, init_noise_mean, init_noise_variance, True), lw=2, color='#d38c9d', label="Noisy signal")
line_filtered, = ax.plot(t, fir_filter(harmonic_with_noise(init_amplitude, init_frequency, init_phase, init_noise_mean, init_noise_variance, True), init_cutoff), lw=2, color='#a55166', label="Filtered signal")

# Легенда для графіків
ax.legend(loc="upper right", fontsize=12, facecolor='#e2b4c1')

# Налаштування слайдерів для зміни параметрів сигналу та шуму
axcolor = 'white'
ax_amp = plt.axes([0.1, 0.22, 0.65, 0.03], facecolor=axcolor)
ax_freq = plt.axes([0.1, 0.17, 0.65, 0.03], facecolor=axcolor)
ax_phase = plt.axes([0.1, 0.12, 0.65, 0.03], facecolor=axcolor)
ax_noise_mean = plt.axes([0.1, 0.07, 0.65, 0.03], facecolor=axcolor)
ax_noise_var = plt.axes([0.1, 0.02, 0.65, 0.03], facecolor=axcolor)
ax_cutoff = plt.axes([0.1, -0.05, 0.65, 0.03], facecolor=axcolor)

# Створення слайдерів для налаштування амплітуди, частоти, фази, середнього значення шуму, дисперсії шуму та частоти відсічення
s_amp = Slider(ax_amp, 'Amplitude', 0.1, 2.0, valinit=init_amplitude, color='#d38c9d')
s_freq = Slider(ax_freq, 'Frequency', 0.1, 5.0, valinit=init_frequency, color='#d38c9d')
s_phase = Slider(ax_phase, 'Phase', -np.pi, np.pi, valinit=init_phase, color='#d38c9d')
s_noise_mean = Slider(ax_noise_mean, 'Noise Mean', -0.5, 0.5, valinit=init_noise_mean, color='#d38c9d')
s_noise_var = Slider(ax_noise_var, 'Noise Variance', 0.01, 0.5, valinit=init_noise_variance, color='#d38c9d')
s_cutoff = Slider(ax_cutoff, 'Cutoff Frequency', 0.1, 5.0, valinit=init_cutoff, color='#d38c9d')

# Створення чекбоксу для перемикання показу шуму
ax_check = plt.axes([0.8, 0.1, 0.1, 0.05], facecolor=axcolor)
check = CheckButtons(ax_check, ['Show Noise'], [True])
show_noise = True

# Функція для перемикання видимості шуму на графіку
def toggle_noise(label):
    global show_noise
    show_noise = not show_noise 
    update(None)  

check.on_clicked(toggle_noise)

# Створення чекбоксу для перемикання застосування фільтра
ax_check_filter = plt.axes([0.8, 0.15, 0.1, 0.05], facecolor=axcolor)
check_filter = CheckButtons(ax_check_filter, ['Apply Filter'], [True])

# Функція для перемикання видимості відфільтрованого сигналу
def toggle_filter(label):
    if label == 'Apply Filter':
        line_filtered.set_visible(check_filter.get_status()[0]) 
        update(None)  

check_filter.on_clicked(toggle_filter)

# Функція для оновлення графіків при зміні значень слайдерів
def update(val):
    global show_noise
    noisy_signal = harmonic_with_noise(s_amp.val, s_freq.val, s_phase.val, s_noise_mean.val, s_noise_var.val, show_noise)  
    filtered_signal = fir_filter(noisy_signal, s_cutoff.val)  
    line.set_ydata(noisy_signal)  
    line_filtered.set_ydata(filtered_signal)  
    fig.canvas.draw_idle() 

# Пов'язуємо функцію оновлення з слайдерами
s_amp.on_changed(update)
s_freq.on_changed(update)
s_phase.on_changed(update)
s_noise_mean.on_changed(lambda val: regenerate_noise(val, s_noise_var.val))  
s_noise_var.on_changed(lambda val: regenerate_noise(s_noise_mean.val, val))  
s_cutoff.on_changed(update)

# Функція для регенерації шуму при зміні параметрів
def regenerate_noise(noise_mean, noise_variance):
    global current_noise
    current_noise = np.random.normal(noise_mean, np.sqrt(noise_variance), len(t))  
    update(None)  

# Створення кнопки скидання значень
ax_reset = plt.axes([0.8, 0.05, 0.1, 0.04], facecolor=axcolor)
button_reset = Button(ax_reset, 'Reset', color='#d38c9d', hovercolor='#e2b4c1')

# Функція для скидання значень параметрів на початкові
def reset(event):
    global current_noise
    s_amp.reset()  
    s_freq.reset() 
    s_phase.reset() 
    s_noise_mean.reset()   
    s_noise_var.reset()  
    s_cutoff.reset() 
    current_noise = np.random.normal(init_noise_mean, np.sqrt(init_noise_variance), len(t))  
    update(None) 

button_reset.on_clicked(reset)

# Налаштування вигляду кнопок і слайдерів
check.rectprops = dict(facecolor='#d38c9d', edgecolor='#a55166', linewidth=2)
check.labelprops = dict(color='#a55166', fontsize=12)
s_amp.label.set_fontsize(12)
s_freq.label.set_fontsize(12)
s_phase.label.set_fontsize(12)
s_noise_mean.label.set_fontsize(12)
s_noise_var.label.set_fontsize(12)
s_cutoff.label.set_fontsize(12)

# Показуємо графік
plt.show()
