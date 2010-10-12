(function() {
	//Load the language file.
	tinymce.PluginManager.requireLangPack('prettify');
	
	tinymce.create('tinymce.plugins.Prettify', {
	
		init : function(ed, url) {
			// Register the command so that it can be invoked by using tinyMCE.activeEditor.execCommand('mceExample');
			ed.addCommand('mcePrettify', function() {
				ed.windowManager.open({
					file : url + '/dialog.htm',
					width : 450  ,
					height : 400 ,
					inline : 1
				}, {
					plugin_url : url
				});
			});

			// Register example button
			ed.addButton('prettify', {
				title : 'prettify.desc',
				cmd : 'mcePrettify',
				image : url + '/img/prettify.gif'
			});

			// Add a node change handler, selects the button in the UI when a image is selected
			ed.onNodeChange.add(function(ed, cm, n) {
				cm.setActive('prettify', n.nodeName == 'IMG');
			});
		},


		createControl : function(n, cm) {
			return null;
		},

		getInfo : function() {
			return {
				longname : 'google code prettify',
				author : 'dengmin',
				authorurl : 'http://www.iyouf.info',
				infourl : 'http://www.iyouf.info',
				version : "1.0"
			};
		}
	});

	// Register plugin
	tinymce.PluginManager.add('prettify', tinymce.plugins.Prettify);
})();