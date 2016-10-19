(function(input_id) {
 var input = document.getElementById(input_id);
 var valids = '0,1,2,3,4,5,6,7,8,9'.split(',');
 var clean = '';
 var spliter = ' ';
 input.oninput = function() {
	 while (input.value.startsWith(spliter)) {
		 input.value = input.value.slice(1);
	 }
	 var current = input.value.slice(-1)
	 if (valids.indexOf(current) < 0) {
		 input.value = input.value.slice(0, -1);
	 } else {
		 clean = input.value.split(spliter).join('');
			if (clean.length > 0 && clean.length < 4) {
				input.value = clean;
			} else if (clean.length >= 4 && clean.length < 7) {
				input.value = [clean.slice(-6, -3), clean.slice(-3)].join(spliter);  
			} else if (clean.length >= 7) {
				input.value = [clean.slice(-9, -6), clean.slice(-6, -3), clean.slice(-3)].join(spliter);  
			}
		}
	};
})("search_input");

