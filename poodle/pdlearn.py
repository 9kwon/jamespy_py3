# Python 3
# import pandalearn.pdlearn as pdl (or poodle)

from sklearn import linear_model, model_selection, cross_validation
import pandas as pd

def grid_scores( grid_scores_):
	"""
	Translate grid_scores_ in sklearn to pd.DataFrame
	Parameters
	----------
	grid_scores_ : sklearn type for grid
	   grid_scores_ generated by sklearn and gs_Ridge.    
	"""
	p_l = list()
	for s in grid_scores_:
		p = pd.DataFrame()
		l = len(s.cv_validation_scores)
		for k in list(s.parameters.keys()):
			p[k] = [s.parameters[k]] * l    
		p["Unit"] = range( l)
		p["Score"] = s.cv_validation_scores
		p_l.append( p)
	p_df = pd.concat( p_l, ignore_index = True)
	return p_df

def read_csv( *args, index_col=0, header=[0,1], **kwargs):
	"""
	Emulation for pandas.DataFrame() 
	Parameters
	----------
	The parameters of Pandas DataFrame are used 
	*args : any type
		 all arguments without a keyword
	**kwargs: any type
		 all arguments without a keyword
	"""
	return DataFrame(pd.read_csv( *args, index_col=index_col, header=header, **kwargs))

class DataFrame( pd.DataFrame):
	def __init__(self, *args, **kwargs):
		"""
		Emulation for pandas.DataFrame()
		Parameters
		----------
		The parameters of Pandas DataFrame are used 
		*args : any type
			 all arguments without a keyword
		**kwargs: any type
			 all arguments without a keyword
		"""
		super().__init__( *args, **kwargs)

	def to_csv_excel( self, ext_s, fname = None, fname_out = None):
		if fname_out is not None:
			super().to_csv( fname_out + '.csv') # index should be stored.
			super().to_excel( fname_out +'.xls') 			
		elif fname is not None:
			fname_out = fname[:-4] + ext_s
			print( 'The saving file name is', fname_out)
			super().to_csv( fname_out +'.csv') 
			super().to_excel( fname_out +'.xls') 			
		print( 'Data is not saved since both fname and fname_out are not provided.')


class GridSearchCV( model_selection.GridSearchCV):
	def __init__(self, fname, estimator = None, param_grid = None, **kwargs):	
		"""
		estimator and param_grid can be values defined in csv. 
		"""
		if estimator is None:
			estimator = linear_model.LinearRegression()
		if param_grid is None:
			param_grid = {}

		super().__init__( estimator, param_grid, **kwargs)

		self.fname = fname

		# 1. Read all data
		self.df = read_csv( fname)

		# 2. Separate data and parameters
		df_data = self.df[["X", "y"]]
		self.df_param = self.df["param"].set_index("index")
		# Later, Nan will be removed
		# Later, comments are separated. 

		# make data to be useful for regression
		self.X = df_data['X'].values
		self.y = df_data['y'].values

		# Later, the parameter part will be used.

	def fit(self):
		return super().fit( self.X, self.y)

	def cross_val_predict(self, fname_out = None):
		"""
		This function is added to save the result of the predicted values. 
		"""
		yp = cross_validation.cross_val_predict( self.best_estimator_, self.X, self.y)

		idx = pd.MultiIndex.from_product([['yp'], self.df['y'].columns])
		yp_df = pd.DataFrame( yp, index = self.df.index, columns=idx)
		df_out_org = self.df.merge( yp_df, left_index = True, right_index = True)
		self.df_out = DataFrame( df_out_org[["X", "y", "yp", "param"]])
		# df_out = pd.concat([self.df, yp_df], axis = 1)

		self.df_out.to_csv_excel( '_out', self.fname, fname_out)		

		return yp