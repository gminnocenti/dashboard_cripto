import pandas as pd
import streamlit as st
import altair as alt
import hashlib
import sqlite3
from LOCAL_ENCRIPTACION_CREDENCIALES import texto_encriptado_credenciales, decrypt_text_credenciales

# Load data
def local_login_respuesta(username_login_interfaz, password_login_interfaz):
    """Esta función se conecta a la tabla login y devuelve el nivel de acceso que le pertenece a cada credencial."""
    # Conectar a la base de datos local
    username_login = username_login_interfaz
    password_login = password_login_interfaz

    username_hash = texto_encriptado_credenciales(username_login)
    password_hash = hashlib.sha256(password_login.encode()).hexdigest()

    cnxn = sqlite3.connect('casamonarca.db')
    cursor = cnxn.cursor()
    
    # Conectar a tabla login, hacer query para ver si la contraseña y username se encuentran en la base de datos
    cursor.execute("SELECT username, password FROM login WHERE username = ? AND password = ?", (username_hash, password_hash))
    user = cursor.fetchone()
    
    cursor.close()
    cnxn.close()

    return user

def main():
    st.title("Visualizacion de Datos Casa Monarca Ayuda Humanitaria al Migrante")

    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False

    if not st.session_state.logged_in:
        username = st.text_input("Usuario")
        password = st.text_input("Contraseña", type="password")
        login_button = st.button("Login")

        if login_button:
            user = local_login_respuesta(username, password)
            if user:
                st.session_state.logged_in = True
                st.session_state.username = username
                st.session_state.password = password
                st.success("Login successful")
            else:
                st.error("Ingrese Correctamente las Credenciales Por Favor")
    else:
        logout_button = st.button("Logout")

        if logout_button:
            st.session_state.logged_in = False
            st.experimental_rerun()
        
        data_path = 'migrants_data.csv'
        df = pd.read_csv(data_path, parse_dates=['Fecha_Atencion', 'Fecha_Nacimiento', 'Fecha_Salida_Pais_Origen', 'Fecha_Ingreso_Mexico'])

        # Sidebar filters
        st.sidebar.header('Filters')
        country_filter = st.sidebar.multiselect('Select Country', df['Pais_Origen'].unique())
        gender_filter = st.sidebar.multiselect('Select Gender', df['Sexo'].unique())
        tipo_filter = st.sidebar.multiselect('Select Adulto_NNA_NNAnA', df['Adulto_NNA_NNAnA'].unique())
        date_range_filter = st.sidebar.date_input('Select Date Range for Fecha_Ingreso_Mexico', [df['Fecha_Ingreso_Mexico'].min(), df['Fecha_Ingreso_Mexico'].max()])
        hospedado_filter = st.sidebar.checkbox('Hospedado Actualmente', False)

        # Convert date_range_filter to datetime
        date_range_filter = [pd.to_datetime(date) for date in date_range_filter]

        # Function to filter data based on sidebar inputs
        def filter_data(data, country_filter, gender_filter, tipo_filter, date_range_filter, hospedado_filter):
            filtered_data = data
            if country_filter:
                filtered_data = filtered_data[filtered_data['Pais_Origen'].isin(country_filter)]
            if gender_filter:
                filtered_data = filtered_data[filtered_data['Sexo'].isin(gender_filter)]
            if tipo_filter:
                filtered_data = filtered_data[filtered_data['Adulto_NNA_NNAnA'].isin(tipo_filter)]
            if date_range_filter:
                filtered_data = filtered_data[(filtered_data['Fecha_Ingreso_Mexico'] >= date_range_filter[0]) & (filtered_data['Fecha_Ingreso_Mexico'] <= date_range_filter[1])]
            if hospedado_filter:
                filtered_data = filtered_data[filtered_data['Hospedado_Actualmente'] == 'Si']
            return filtered_data

        # Apply filters
        filtered_df = filter_data(df, country_filter, gender_filter, tipo_filter, date_range_filter, hospedado_filter)

        # Sidebar filter for age range
        age_range_filter = st.sidebar.slider('Select Age Range', int(filtered_df['Edad'].min()), int(filtered_df['Edad'].max()), (int(filtered_df['Edad'].min()), int(filtered_df['Edad'].max())))

        # Function to filter data based on age range
        def filter_data_by_age_range(data, age_range):
            filtered_data = data[(data['Edad'] >= age_range[0]) & (data['Edad'] <= age_range[1])]
            return filtered_data

        # Apply age range filter
        filtered_df = filter_data_by_age_range(filtered_df, age_range_filter)

        #####
        # Descriptive Dashboard

        # Function to create histograms using Altair
        def create_histogram(data, column):
            chart = alt.Chart(data).mark_bar().encode(
                x=alt.X(column, bin=alt.Bin(maxbins=20)),
                y='count()',
            ).properties(
                title=f'Histograma of {column}'
            )
            return chart

        # Function to create bar charts using Altair
        def create_bar_chart(data, column):
            chart = alt.Chart(data).mark_bar().encode(
                x=alt.X(column, sort='-y'),
                y='count()',
            ).properties(
                title=f'Bar Chart of {column}',
                width=400,
            )
            return chart

        # Function to create time series plots using Altair
        def create_time_series(data, x_column):
            chart = alt.Chart(data).mark_line().encode(
                x=x_column,
                y='count()'
            ).properties(
                width=700,
                height=400
            )
            return chart

        # Function to create bar charts for binary variables using Altair
        def create_binary_bar_chart(data, column):
            chart = alt.Chart(data).mark_bar().encode(
                x=alt.X(column),
                y='count()',
                color=alt.Color(column, scale=alt.Scale(domain=['Si', 'No'], range=['#a23516', '#ef8b68'])),
            ).properties(
                title=f'Binary Bar Chart of {column}',
                width=400,
            )
            return chart

        # Function to create histograms using Altair
        def create_histogram_date(data, column):
            chart = alt.Chart(data).mark_bar().encode(
                x=alt.X(column, bin=alt.Bin(maxbins=20), axis=alt.Axis(labelAngle=90, format='%Y-%m-%d')),
                y='count()',
            ).properties(
                title=f'Histogram of {column}'
            )
            return chart

        def plot_bar(column, data):
            chart = alt.Chart(data).mark_bar().encode(
                x=alt.X(column, type='nominal'),
                y=alt.Y('count()', title='Count')
            ).properties(
                title=f'Numero de personas para la columna {column}'
            )
            st.altair_chart(chart, use_container_width=True)

        # Function to plot and display histograms using Altair
        def plot_hist(column, data):
            chart = alt.Chart(data).mark_bar().encode(
                x=alt.X(column, bin=alt.Bin(maxbins=30), title=column),
                y=alt.Y('count()', title='Count')
            ).properties(
                title=f'Numero de personas para la columna {column}'
            )
            st.altair_chart(chart, use_container_width=True)

        #####
        # Create expanders for each type of chart
        with st.expander('Personas Hospedades en la casa'):
            # Filter rows where Hospedado_Actualmente is 'Si'
            activo = filtered_df[filtered_df['Hospedado_Actualmente'] == 'Si']

            # Select specific columns
            result = activo[['Sexo', 'Edad', 'Pais_Origen', 'Tipo_Poblacion']]
            st.subheader('Sexo')
            plot_bar('Sexo', result)

            st.subheader('Edad')
            plot_hist('Edad', result)

            st.subheader('Pais_Origen')
            plot_bar('Pais_Origen', result)

            st.subheader('Tipo_Poblacion')
            plot_bar('Tipo_Poblacion', result)

        with st.expander('Datos Historicos'):
            st.subheader('Numero de Personas por Edad')
            int_vars = ['Edad']
            for var in int_vars:
                st.altair_chart(create_histogram(filtered_df, var), use_container_width=True)

            st.subheader('Variables Categoricas')
            cat_vars = ['Adulto_NNA_NNAnA', 'Pais_Origen', 'Departamento_Estado', 'Estado_Civil', 'Tipo_Poblacion', 'Grado_Estudio', 'Idiomas_Domina', 'Ingreso_Mexico_Por', 'Destino_Final', 'Servicios_Brindados'] #En vez de tipo, Adulto, NNA, NNAnA
            for var in cat_vars:
                st.altair_chart(create_bar_chart(filtered_df, var), use_container_width=True)

            st.subheader('Temporal Variables')
            date_vars = ['Fecha_Atencion', 'Fecha_Nacimiento', 'Fecha_Salida_Pais_Origen', 'Fecha_Ingreso_Mexico']
            for var in date_vars:
                chart = create_time_series(filtered_df, var)
                st.altair_chart(chart, use_container_width=True)

            st.subheader('Binary Variables')
            binary_vars = ['Hijos', 'Leer_Escribir', 'Viajo_Con_Alguien', 'Abuso_Derechos_Humanos_Antes_Mexico', 'Abuso_Derechos_Humanos_Al_Llegar_Mexico']
            for var in binary_vars:
                st.altair_chart(create_binary_bar_chart(filtered_df, var), use_container_width=True)

            ####
            # Calcular la cantidad acumulada de personas que llegan a la casa de migrantes para cada fecha
            arrivals_per_date = filtered_df.groupby('Fecha_Ingreso_Mexico').size().reset_index(name='Cantidad_Personas')
            arrivals_per_date['Cantidad_Acumulada'] = arrivals_per_date['Cantidad_Personas'].cumsum()

            # Crear el gráfico de series temporales
            time_series_chart = alt.Chart(arrivals_per_date).mark_line().encode(
                x=alt.X('Fecha_Ingreso_Mexico:T', title='Fecha de Ingreso a México'),
                y=alt.Y('Cantidad_Acumulada:Q', title='Cantidad Acumulada de Personas')
            ).properties(
                width=700,
                height=400,
                title='Cantidad Acumulada de Personas que Llegan a la Casa de Migrantes por Fecha'
            )

            # Mostrar el gráfico
            st.altair_chart(time_series_chart, use_container_width=True)

main()
