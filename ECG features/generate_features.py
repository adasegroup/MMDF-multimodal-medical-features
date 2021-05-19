from scipy import signal
from scipy import integrate
import numpy as np
import neurokit2 as nk


def calculate_features(a):
    array = np.array(a)
    mean = np.mean(array)
    maximum = np.max(array, initial=0)
    minimum = np.min(array, initial=0)
    std = np.std(array)
    median = np.median(array)
    return np.array([mean, maximum, minimum, std, median])

def p_peak_features(ecg_signal, waves):
    
    biphase = []
    areas = []
    t_till_peaks = []
    ampls = []
    dur = []
    idxs = []
    pq_intervals = []

    for start_p, end_p, start_q in zip(waves['ECG_P_Onsets'], waves['ECG_P_Offsets'], waves['ECG_R_Offsets']):

        try:
            p_peak = ecg_signal[start_p:end_p]
            peaks, _ = signal.find_peaks(p_peak)

            pq_interval = ecg_signal[start_p:start_q].shape[0] * 2
            pq_intervals.append(pq_interval)

            biphase_p = peaks.shape[0]
            biphase.append(biphase_p)

            duration = p_peak.shape[0] * 2
            dur.append(duration)

            area_under_p = integrate.simps(p_peak)
            areas.append(area_under_p)

            amplitude = np.max(p_peak) - np.min(p_peak)
            ampls.append(amplitude)

            time_till_peak_p = peaks[0] * 2
            t_till_peaks.append(time_till_peak_p)

            index_value = integrate.simps(p_peak) / (p_peak.shape[0] * 2)
            idxs.append(index_value)
            
        except TypeError:
            pass
        
    return biphase, areas, t_till_peaks, ampls, dur, idxs, pq_intervals

def get_general_features(header):
    for iline in header:
        if iline.startswith('#Age'):
            tmp_age = iline.split(': ')[1].strip()
            age = int(tmp_age if tmp_age != 'NaN' else None)
        elif iline.startswith('#Sex'):
            tmp_sex = iline.split(': ')[1]
            if tmp_sex.strip()=='Female':
                sex =1
            else:
                sex=0
    return age, sex

def generate_features(ecg, header):
    #input: 12-lead ecg and its header
    num_leads = len(ecg)
    fs = 500
    features = []
    
    for ecg_signal, ecg_info in zip(ecg, header[:13]):
        
        features_for_single_lead = []
        ecg_cleaned = nk.ecg_clean(ecg_signal, sampling_rate = fs)
        
        if np.all((ecg_cleaned == 0)):
            return None        
        else:
            _, rpeaks = nk.ecg_peaks(ecg_cleaned, sampling_rate = fs)                      
    
            if rpeaks['ECG_R_Peaks'].size == 0:
                return None            
            else:
                try:                    
                    signal_dwt, waves_dwt = nk.ecg_delineate(ecg_cleaned, rpeaks['ECG_R_Peaks'], sampling_rate=fs, method="dwt")
                    biphase, areas, t_till_peaks, ampls, dur, idxs, pq_intervals = p_peak_features(ecg_cleaned, waves_dwt) 
                    features_for_single_lead.append([calculate_features(pq_intervals), calculate_features(dur), 
                                                     calculate_features(idxs),calculate_features(areas), calculate_features(ampls), 
                                                     calculate_features(t_till_peaks), calculate_features(biphase)])                     
                except IndexError:
                    return None
                
        age, sex = get_general_features(header)
        features.append(np.array([features_for_single_lead, age, sex]))

    return np.array(features)