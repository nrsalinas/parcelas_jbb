################################################################################
#
# This program is free software: you can redistribute it and/or modify it under 
# the terms of the GNU General Public License as published by the Free Software 
# Foundation, either version 3 of the License, or (at your option) any later 
# version.
# 
# This program is distributed in the hope that it will be useful, but WITHOUT 
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS 
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License along with 
# this program. If not, see <https://www.gnu.org/licenses/>. 
#
# Copyright 2025 Nelson R. Salinas
#
################################################################################

import streamlit as st
import pandas as pd
import gspread
import datetime

gc = gspread.service_account_from_dict(st.secrets.credentials)

if 'errors' not in st.session_state:
	st.session_state.errors = ''

if 'site_ok' not in st.session_state:
	st.session_state.site_ok = False

if 'submitted' not in st.session_state:
	st.session_state.submitted = False


##########     Object lists    ##############
#listas = pd.read_csv("Lista_categorias.csv")
tabla_sitios = pd.read_csv("sitios.csv")
sitios = tabla_sitios.sitio.tolist()

wise_people = ['Lina Corrales', 'Esther Velásquez', 'Lina y Esther']

digitizers = ['Lina Corrales', 'Esther Velásquez']

id_observaciones = []

st.markdown("""

# Jardín Botánico de Bogotá

## Programa Conservación _in situ_

### Formato de digitalización de transectos de vegetación.

#### Instrucciones

Insertar las observaciones en la forma abajo. Una vez termine de digitar los datos de una observación, presione el botón :red[**Validar**] para validar los datos. Si existen errores, un mensaje aparecerá indicando la naturaleza del error. Los datos no serán guardados si son erróneos, así que deben ser corregidos para que puedan ser guardados.

""")

# This doesn't work in Linux -> :blue-background[:red[**Enviar**]] 

def validate_site():

	in_trouble = False

	if st.session_state.date is None:
		#st.info('Error: Falta fecha de observación.', icon="🔥")
		st.session_state.errors += 'La fecha es un campo obligatorio.\n\n'
		in_trouble = True

	if st.session_state.resp is None:
		st.session_state.errors += 'El nombre del responsable es un campo obligatorio.\n\n'
		in_trouble = True

	if st.session_state.digitizer is None:
		st.session_state.errors += 'El digitador es un campo obligatorio.\n\n'
		in_trouble = True

	if st.session_state.lon is None or st.session_state.lat is None:
		st.session_state.errors += "Las coordenadas geográficas son obligatorias.\n\n"
		in_trouble = True

	if st.session_state.site is None:
		st.session_state.errors += "El sitio es un campo obligatorio.\n\n"
		in_trouble = True

	if in_trouble == False:
		st.session_state.site_ok = True


def validate_rec():
	st.session_state.errors = ""
	
	if st.session_state.ind is None:
		st.session_state.errors += 'El número de individuo es un campo obligatorio.\n\n'

	if st.session_state.morfo is None:	
		st.session_state.errors += 'El morfo o descripción de campo es un dato obligatorio.\n\n'


def set_site():
	st.session_state.site_ok = True


def submit():
	
	sh = gc.open_by_key(st.secrets.table_link).worksheet(st.session_state.digitizer)
	now = datetime.datetime.now()
	row = [
		str(st.session_state.date),
		st.session_state.photo.name,
		st.session_state.observer,
		st.session_state.sp1,
		st.session_state.sp2,
		st.session_state.inter,
		st.session_state.part,
		st.session_state.lat,
		st.session_state.lon,
		st.session_state.site,
		now.strftime('%Y-%m-%d %H:%M:%S'),
		st.session_state.digitizer,
	]
	sh.append_row(row)
	st.session_state.submitted = True

def submit_ind():
	st.session_state.ind_data = st.empty()


with st.form(
	"Transecto - sitio",
	clear_on_submit=False,
	):

	st.selectbox(
		"Responsable", 
		wise_people, 
		index=None, 
		key='resp',
		placeholder="Seleccione un investigador",
		help='Persona que se encargó de dirigir la operación'
	)

	st.selectbox(
		"Digitador", 
		digitizers, 
		index=None, 
		key='digitizer',
		placeholder="Seleccione un investigador",
		help='Persona que se encargó de digitar el formulario'
	)

	st.date_input(
		"Fecha",
		help="Fecha en la cual fue levantado el transecto.",
		value=None,
		key="date",
	)

	st.time_input(
		"Hora inicio",
		value=None,
		key="time0",
		step=900, # in secs : 15 mins
		help="Hora de inicio del transecto, en formato 24 horas."
	)

	st.time_input(
		"Hora final",
		value=None,
		key="timef",
		step=900, # in secs : 15 mins
		help="Hora de finalización del transecto, en formato 24 horas."
	)

	st.selectbox(
		"Sitio", 
		sitios, 
		index=None, 
		key='site',
		placeholder='Nombre del sitio de muestreo',
		help='Nombre estandarizado del lugar de muestreo'
	)

	st.text_input(
		"Sector",
		key='sector',
		placeholder='Sector de muestreo',
		help='Nombre del sector de muestreo'
	)

	st.number_input(
		"Latitud", 
		key="lat",
		value=None,
		placeholder="Latitud",
		help='Latitud de ubicación del transecto en formato decimal (e.g., 3.09284)',
		max_value=4.838990,
		min_value=3.725902
	)

	st.number_input(
		"Longitud", 
		key="lon",
		value=None,
		placeholder="Longitud",
		help='Longitud de ubicación del transecto en formato decimal (e.g., -77.2360184)',
		min_value=-74.2248,
		max_value=-73.99194,
	)

	st.form_submit_button('Validar', on_click=validate_site)

if len(st.session_state.errors) > 0:
	st.session_state.errors = "# Error\n\n#" + st.session_state.errors
	st.info(st.session_state.errors)

if st.session_state.site_ok:

	with st.form(
		"Transecto - registros",
		clear_on_submit=True
	):
	
		st.number_input(
			"Individuo",
			key='ind',
			value=None,
			step=1,
			placeholder="Número de individuo",
			help='Identificador del individuo en el transecto',
		)

		st.text_input(
			"Morfo",
			key='morfo',
			placeholder='Morfo',
			help='Descripción o identificación de campo de la especie.'
		)

		st.form_submit_button('Validar', on_click=validate_rec)

	if len(st.session_state.errors) > 0:
		st.session_state.errors = "# Error\n\n#" + st.session_state.errors
		st.info(st.session_state.errors)

exit(0)