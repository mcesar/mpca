var fs = require('fs');
var recursive = require('recursive-readdir');
var db = require('./db');
var constants = require('./constants');

var count = -1;

console.log('Excluindo clusters_entidades');
db.query('delete from clusters_entidades', function (err, results) {
	if (err) { throw err; }
	console.log('Excluindo clusters');
	db.query('delete from clusters', function (err, results) {
		if (err) { throw err; }
		console.log('Incluindo clusters');
		recursive(__dirname, function (err, files) {
			import_files(files);
		});
	});
});

function import_files(files) {
	var arr, repository, file, name, content, regexCluster, regexEntity, clusters, entities, count, i;
	regexCluster = /subgraph (.+) {/;
	regexEntity = /\"(\d+)\"\[/;
	clusters = [];
	for (i = 0; i < files.length; i += 1) {
		if (/\.dot$/.test(files[i])) {
			arr = files[i].replace(__dirname, '').split('/');
			repository = constants.repositorioMap[arr[arr.length-2]];
			file = arr[arr.length-1];
			content = fs.readFileSync(files[i],{ encoding: 'utf8'}).split('\n');
			for (var j = 0; j < content.length; j++) {
				if (regexCluster.test(content[j])) {
					name = regexCluster.exec(content[j])[1];
					entities = [];
					clusters.push({ repository: repository, file: file, name: name, entities: entities });
				} else if (regexEntity.test(content[j])) {
					entities.push(regexEntity.exec(content[j])[1]);
				}
			}
		}
	}

	for (i = 0; i < clusters.length; i += 1) {
		db.query('insert into clusters(repositorio, arquivo, nome) values (?,?,?)',
			[clusters[i].repository, clusters[i].file, clusters[i].name],
			function (err, results) {
				if (err) throw err;
				var clusterId = results.insertId;
				for (var j = 0; j < clusters[i].length; j++) {
					if (count == -1) {
						count = 0;
					}
					count++;
					db.query('insert into clusters_entidades(cluster, entidade) values (?,?)',
						[clusterId, clusters[i][j]],
						function (err, results) {
							if (err) throw err;
							count--;
						}
					);
				};
			}
		);
	}
}

var timer = setInterval(function () {
	if (count == 0) {
		db.end();
		clearInterval(timer);
	}
}, 500);