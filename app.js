var fs = require('fs');
var exec = require('child_process').exec;
var db = require('./db');

var commits = fs.readFileSync(__dirname + '/log.csv').toString().split('\n');

db.query('delete from entidades', function (err, results, close) {
	if (err) { throw err; }
	close();
	db.query('delete from commits', function (err, results, close) {
		if (err) { throw err; }
		next(0);
	});
});

function next (i) {
	if (i >= commits.length) {
		console.log('ok');
		return;
	}
	var arr = commits[i].split('\t');
	arr[2] = arr[2].replace(' +0000', '');

	db.query('insert into commits(id,autor,data,comentario) values (?,?,?,?)', 
		arr,
		function (err, results, close) {
			if (err) { throw err; }
			close();
			insereEntidades(arr[0]);
		}
	);

	function insereEntidades (commit) {
		exec('git diff-tree --no-commit-id --name-only -r ' + arr[0], 
			{cwd:'../historage-data2'}, 
			function (err, stdout, stderr) {
				var lines = stdout.split('\n');
				(function nextLine (j) {
					if (j >= lines.length) {
						next(i + 1);
						return;
					}
					if (lines[j].indexOf('.f/') !== -1) {
						db.query('insert into entidades(caminho,commit) values (?,?)', 
							[lines[j], commit],
							function (err, results, close) {
								if (err) { throw err; }
								close();
								nextLine(j+1);
							}
						);					
					} else {
						nextLine(j+1);
					}
				})(0);
			}
		);
	}
};