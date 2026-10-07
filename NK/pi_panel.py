"""Streamlit PI mode, including explicit source/training mapping confirmation."""
import json
from pathlib import Path
import streamlit as st
import pandas as pd
from pi_input import ROOT, FEATURES, Settings, CollectorReader, InputError, verified_registry, load_mapping, build_features


def render_pi_mode(predictor, display):
    try:
        settings=Settings.load(); mapping=load_mapping(); registry=verified_registry()
    except Exception as ex:
        st.error('Konfigurasi PI Collector tidak dapat dimuat: '+type(ex).__name__)
        return
    st.caption('Input berasal dari snapshot tersimpan PI Collector. Riwayat prediksi hanya disimpan pada sesi ini.')
    try:
        attrs=CollectorReader(settings).get('/attributes')
        if not isinstance(attrs,list): raise InputError('Format atribut tidak valid.')
        eligible={a['attribute_id']:a for a in attrs if isinstance(a,dict) and a.get('attribute_id') in registry and a.get('web_id')==registry[a['attribute_id']]['web_id']}
    except InputError as ex:
        st.error(str(ex)); return
    with st.expander('Pemetaan 13 fitur ke atribut PI', expanded=any(m.get('status')!='verified' for m in mapping['features'].values())):
        st.info('Pilih atribut, isi satuan persis seperti data training, lalu konfirmasi kesesuaiannya dengan bukti. Kandidat nama belum membuktikan kesesuaian fitur.')
        with st.form('pi_mapping_form'):
            edited={'version':1,'features':{}}
            for feature in FEATURES:
                m=mapping['features'][feature]
                st.markdown('**'+feature+'**')
                candidates=[i for i in m.get('candidates',[]) if i in eligible]
                options=['']+candidates+sorted(i for i in eligible if i not in candidates)
                if candidates:
                    st.caption('Kandidat berdasarkan nama: '+', '.join(eligible[i].get('business_name',i) for i in candidates))
                selected=m.get('attribute_id') if m.get('attribute_id') in eligible else ''
                ident=st.selectbox('Atribut PI',options,index=options.index(selected),key='map_'+feature,format_func=lambda i: 'Belum dipetakan' if not i else eligible[i].get('equipment','')+' / '+eligible[i].get('business_name',i)+' / '+(eligible[i].get('position') or ''))
                c1,c2=st.columns(2)
                source=c1.text_input('Satuan sumber',value=m.get('source_unit',''),key='source_'+feature)
                target=c2.text_input('Satuan data training',value=m.get('training_unit',''),key='target_'+feature)
                evidence=st.text_input('Referensi bukti pemetaan dan satuan',value=m.get('evidence_ref',''),key='evidence_'+feature)
                confirmed=st.checkbox('Saya mengonfirmasi atribut dan satuannya sesuai fitur training',value=m.get('status')=='verified',key='confirmed_'+feature)
                edited['features'][feature]={'attribute_id':ident or None,'source_unit':source.strip(),'training_unit':target.strip(),'evidence_ref':evidence.strip(),'source_unit_confirmed':confirmed,'status':'verified' if confirmed and ident and source.strip() and target.strip() and evidence.strip() else 'unknown','candidates':m.get('candidates',[])}
            save=st.form_submit_button('Simpan pemetaan')
        if save:
            path=ROOT/'pi_feature_mapping.json'; tmp=path.with_suffix('.tmp')
            tmp.write_text(json.dumps(edited,indent=2)+'\n');tmp.replace(path)
            st.success('Pemetaan tersimpan.');mapping=edited
    auto=st.toggle('Refresh otomatis dari PI Collector',value=False,key='pi_auto_refresh')
    st.caption(f'Batas umur data: {settings.max_age} detik · selisih timestamp maksimum: {settings.max_skew} detik')

    @st.fragment(run_every=settings.refresh if auto else None)
    def predictions():
        st.button('Ambil data terbaru',key='pi_fetch')
        # Each refresh gets fresh snapshots and revalidates the saved mapping.
        try:
            current=load_mapping(); attributes,snapshots=CollectorReader(settings).read()
            batch=build_features(current,attributes,snapshots,settings,registry)
        except (InputError, OSError, ValueError) as ex:
            st.error(str(ex) if isinstance(ex,InputError) else 'Konfigurasi PI tidak valid.')
            return
        st.dataframe(pd.DataFrame(batch.rows),hide_index=True,width='stretch')
        if batch.values is None:
            st.warning('Prediksi otomatis belum tersedia. Lengkapi pemetaan atau perbaiki data yang ditandai pada tabel. Mode Manual tetap tersedia.')
            for message in batch.errors:
                if message.startswith('Waktu sumber'): st.error(message)
            return
        prediction,confidence=predictor.predict(batch.values)
        if prediction is None: return
        st.success('13 fitur lengkap dan lolos validasi.')
        display(prediction,confidence,batch.values,FEATURES)
        fingerprint=tuple((r['Atribut'],r['Waktu sumber'],r['Nilai']) for r in batch.rows)
        if st.session_state.get('pi_last_fingerprint')!=fingerprint:
            st.session_state.pi_last_fingerprint=fingerprint
            history=st.session_state.setdefault('pi_prediction_history',[])
            history.append({'source':'pi_collector','prediction':float(prediction),'timestamps':[r['Waktu sumber'] for r in batch.rows],'inputs':batch.values})
            del history[:-50]
        st.download_button('Unduh riwayat prediksi PI',json.dumps(st.session_state.get('pi_prediction_history',[]),indent=2),file_name='nk_pi_predictions.json',mime='application/json')
    predictions()
