from flask import Flask, render_template, request, redirect, jsonify
import numpy as np
import sys,urllib2,json,time
from datetime import date
from bokeh.sampledata import us_states as us_states_o
from bokeh.plotting import figure, show, output_file
from bokeh.embed import components
from bokeh.plotting import figure

us_states = us_states_o.data.copy()

del us_states["HI"]
del us_states["AK"]

state_xs = [us_states[code]["lons"] for code in us_states]
state_ys = [us_states[code]["lats"] for code in us_states]

product_map = {"701111":"Flour, white, all purpose, per lb. (453.76 gm)"
			  ,"701312":"Rice, white, long grain, uncooked, per lb. (453.6 gm)"
			  ,"702111":"Bread, white, pan, per lb. (453.6 gm)"
			  ,"703112":"Ground beef, 100% beef, per lb. (453.6 gm)"
			  ,"703613":"Steak, sirloin, USDA Choice, boneless, per lb. (453.6 gm)"
			  ,"704111":"Bacon, sliced, per lb. (453.6 gm)"
			  ,"705111":"Frankfurters, all meat or all beef, per lb. (453.6 gm)"
			  ,"706111":"Chicken, fresh, whole, per lb. (453.6 gm)"
			  ,"707111":"Tuna, light, chunk, per lb. (453.6 gm)"
			  ,"708111":"Eggs, grade A, large, per doz."
			  ,"709112":"Milk, fresh, whole, fortified, per gal. (3.8 lit)"
			  ,"710111":"Butter, salted, grade AA, stick, per lb. (453.6 gm)"
			  ,"710122":"Yogurt, natural, fruit flavored, per 8 oz. (226.8 gm)"
			  ,"711111":"Apples, Red Delicious, per lb. (453.6 gm)"
			  ,"712112":"Potatoes, white, per lb. (453.6 gm)"
			  ,"715211":"Sugar, white, all sizes, per lb. (453.6 gm)"
			  ,"716141":"Peanut butter, creamy, all sizes, per lb. (453.6 gm)"
			  ,"717311":"Coffee, 100%, ground roast, all sizes, per lb. (453.6 gm)"
			  ,"720311":"Wine, red and white table, all sizes, any origin, per 1 liter (33.8 oz)"
			  ,"72511":"Fuel oil per gallon (3.785 liters)"
			  ,"72610":"Electricity per KWH"
			  ,"7471A":"Gasoline, all types, per gallon/3.785 liters"}

def plot_product(pid):



	region_map = {'NE':'0100','MW':'0200','S':'0300','W':'0400'}
	state_region_map = {'CT':'NE', 'ME':'NE', 'MA':'NE', 'NH':'NE', 'NJ':'NE','NY':'NE', 'PA':'NE', 'RI':'NE', 'VT':'NE',\
	'IL':'MW','IN':'MW','IA':'MW','MI':'MW','MN':'MW','NE':'MW','ND':'MW','OH':'MW','SD':'MW','WI':'MW','MO':'MW','KS':'MW',\
	'AK':'W', 'AZ':'W', 'CA':'W', 'CO':'W', 'HI':'W', 'ID':'W', 'MT':'W', 'NV':'W', 'NM':'W', 'OR':'W', 'UT':'W', 'WA':'W','WY':'W',\
	'AL':'S', 'AR':'S', 'DE':'S', 'DC':'S', 'FL':'S', 'GA':'S', 'KY':'S', 'LA':'S', 'MD':'S', 'MS':'S', 'NC':'S', 'OK':'S', 'SC':'S', 'TN':'S', 'TX':'S', 'VA':'S', 'WV':'S'}


	colors = ["#F1EEF6", "#D4B9DA", "#C994C7", "#DF65B0", "#DD1C77", "#980043"]
	region_results = {}
	region_values = {}
	region_dates = {}
	max_value = 0.
	min_value = 1000000.
	for region in region_map:
		try:
			req = urllib2.Request('https://www.quandl.com/api/v3/datasets/BLSI/APU%s%s.json?api_key=xW_u6KfqqkMvKyi4xtwa'%(region_map[region],pid))
			response = urllib2.urlopen(req)
			
			sys.stdout.flush()
			d = json.loads(response.read())

			price_data = np.array(d['dataset']['data'])
			price_dataI = np.argsort(price_data[:,0])[::-1]
			pricedate = "("+str(price_data[price_dataI[0],0])+")"
			value = price_data[price_dataI[0],1]


			region_results[region] = float(value)
			region_dates[region] = pricedate
			region_values[region] = '$'+'%.2f'%float(value)
			if float(value) < min_value:
				min_value = float(value)
			if float(value) > max_value:
				max_value = float(value)
		except Exception,e: 
			print str(e)
			sys.stdout.flush()
			region_results[region] = None
			region_values[region] = 'NA'
			region_dates[region] = ''
	print min_value,max_value
	sys.stdout.flush()


	colors = ["#F1EEF6", "#D4B9DA", "#C994C7", "#DF65B0", "#DD1C77", "#980043"]

	state_colors = []

	
	sys.stdout.flush()
	for state_id in us_states:
		try:
			idx = int(np.round((region_results[state_region_map[state_id]]-min_value)/(max_value-min_value)*5))
			state_colors.append(colors[idx])
		except:
			print 'Bad region!'
			sys.stdout.flush()
			state_colors.append("#CCCCCC")

	p = figure(title="Product Prices by Region", tools="pan",toolbar_location="left",plot_width=1100, plot_height=700)
	p.patches(state_xs, state_ys, fill_color=state_colors, fill_alpha=0.7,line_color="white", line_width=0.5)
	p.patches(state_xs, state_ys, fill_alpha=0.0,line_color="#884444", line_width=2)


	p.text(-93,42.5,text=[region_values['MW']],text_font_size="16pt", text_align="center", text_baseline="middle",text_color="#333333")
	p.text(-93,41.7,text=[region_dates['MW']],text_font_size="9pt", text_align="center", text_baseline="middle",text_color="#333333")

	p.text(-112,40,text=[region_values['W']],text_font_size="16pt", text_align="center", text_baseline="middle",text_color="#333333")
	p.text(-112,39.2,text=[region_dates['W']],text_font_size="9pt", text_align="center", text_baseline="middle",text_color="#333333")

	p.text(-86,33,text=[region_values['S']],text_font_size="16pt", text_align="center", text_baseline="middle",text_color="#333333")
	p.text(-86,32.2,text=[region_dates['S']],text_font_size="9pt", text_align="center", text_baseline="middle",text_color="#333333")

	p.text(-75,43.5,text=[region_values['NE']],text_font_size="16pt", text_align="center", text_baseline="middle",text_color="#333333")
	p.text(-75,42.7,text=[region_dates['NE']],text_font_size="9pt", text_align="center", text_baseline="middle",text_color="#333333")

	script, div = components(p)

	return script,div



app = Flask(__name__)

@app.route('/')
def main():
	return redirect('/index')

@app.route('/index')
def index():
	return render_template('index.html')

@app.route('/productmap',methods=['GET', 'POST'])
def productmap():
	if request.method == 'POST':
		productcode = request.form.get('productcode')
		script,div = plot_product(productcode)

		return render_template('graph.html', script=script, div=div, title=product_map[productcode])
	else:
		return render_template('index.html')


if __name__ == '__main__':
	app.run(debug=True,port=33507)
