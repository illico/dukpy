# encoding: utf-8

"""WebAssets integration for Babel as executed in Python using Dukpy."""

from __future__ import unicode_literals

import os

from dukpy.webassets.common import DukpyFilter, register


@register
class BabelJS(DukpyFilter):
	# WebAssets filter metadata.
	name = 'babeljs'
	options = {'presets': "BABEL_PRESETS", 'loader': 'BABEL_MODULES_LOADER'}
	max_debug_level = None
	
	# Dukpy filter configuration.
	PREPARE = [
			'dukpy.webassets:js/babel.min.js',
			'''
				var process = function(source, options) {
					var result = Babel.transform(source, options);
					var map = result.map ? result.map.toString() : null;
					return { code: result.code, map: map };
				};
			'''
		]
	
	def setup(self):
		super(BabelJS, self).setup()
		
		if not self.presets:  # Assign the default preset list.
			self.presets = []
		elif not isinstance(self.presets, list):
			self.presets = [i.strip() for i in self.presets.split(',')]
	
	def input(self, _in, out, **kw):
		code = _in.read()
		options = {'presets': self.presets, 'filename': os.path.basename(kw['source_path'])}
		
		if self.loader == 'systemjs':
			options['plugins'] = ['transform-es2015-modules-systemjs']
		elif self.loader == 'umd':
			options['plugins'] = ['transform-es2015-modules-umd']
		
		result = self.js.evaljs('eval(process.apply(this, [dukpy.source, dukpy.options]));',
				source=code, options=options)
		
		# TODO: Do something with the sourcemap.
		
		out.write(result['code'])  # Write the result to the destination.

