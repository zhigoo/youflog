tinyMCEPopup.requireLangPack();

var PrettifyDialog = {
  init : function() {
  },

  insert : function() {
    var f = document.forms[0], textarea_output, options = '';

    //If no code just return.
    if(f.syntax_code.value == '') {
      tinyMCEPopup.close();
      return false;
    }

    textarea_output = '<pre class="prettyprint">';
    textarea_output +=  tinyMCEPopup.editor.dom.encode(f.syntax_code.value);
    textarea_output += '</pre> ';
    tinyMCEPopup.editor.execCommand('mceInsertContent', false, textarea_output);
    tinyMCEPopup.close();
  }
};

tinyMCEPopup.onInit.add(PrettifyDialog.init, PrettifyDialog);