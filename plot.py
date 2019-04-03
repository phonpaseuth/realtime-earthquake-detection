from obspy import read

st = read('2019/CI/HEC/BHE.D/CI.HEC..BHE.D.2019.086')

print(st)
st.plot(method='full')
