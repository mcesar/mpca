var fs = require('fs');
var recursive = require('recursive-readdir');
var db = require('./db');
var constants = require('./constants');

/*
console.log('Excluindo commits_issues');
db.query('delete from clusters_entidades', function (err, results) {
	if (err) { throw err; }
	db.query('delete from clusters', function (err, results) {
		if (err) { throw err; }
*/
		recursive(__dirname, function (err, files) {
			import_files(files);
		});
/*
	});
});
*/

function import_files(files) {
	var arr, repository, file, name, content, regex, i;
	regex = /subgraph (.+) {/;
	for (i = 0; i < files.length; i += 1) {
		if (/\.dot$/.test(files[i])) {
			arr = files[i].replace(__dirname, '').split('/');
			repository = constants.repositorioMap[arr[arr.length-2]];
			file = arr[arr.length-1];
			content = fs.readFileSync(files[i],{ encoding: 'utf8'}).split('\n');
			for (var j = 0; j < content.length; j++) {
				if (regex.test(content[j])) {
					name = regex.exec(content[j])[1];
					db.query('insert into clusters(repositorio, arquivo, nome) values (?,?,?)',
						[repository, file, name],
						function (err, results) {
							if (err) throw err;
						}
					);
				}
			};
		}
	}
}