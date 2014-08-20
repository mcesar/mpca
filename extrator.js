var fs = require('fs');
var exec = require('child_process').exec;
var db = require('./db');

var entidades = [];
var mapaDeEntidades = {};

var commits = fs.readFileSync(__dirname + '/log.csv').toString().split('\n');

console.log('Excluindo commits_issues');
db.query('delete from commits_issues', function (err, results) {
	if (err) { throw err; }
	console.log('Excluindo commits_entidades');
	db.query('delete from commits_entidades', function (err, results) {
		if (err) { throw err; }
		console.log('Excluindo entidades');
		db.query('delete from entidades', function (err, results) {
			if (err) { throw err; }
			console.log('Excluindo commits');
			db.query('delete from commits', function (err, results) {
				if (err) { throw err; }
				console.log('Incluindo commits');
				nextCommit(0);
			});
		});
	});
});

function nextCommit (i) {
	if (i >= commits.length) {
		console.log('\nIncluindo entidades');
		proximaEntidade(0);
		return;
	}
	if (i % 100 === 0) {
		process.stdout.write('.');
	}
	var arr = commits[i].split('\t');
	arr[2] = arr[2].replace(' +0000', '');
	
	var commit = arr[0];
	var issues = arr[3].match(/#(\d+)/g);
	var sql = 'insert into commits(id,autor,data,comentario) values (?,?,?,?)';


	db.query(sql, arr, function (err, result) {
		if (err) { throw err; }
		var sql = '', values = [], j;
		if (!!issues) {
			issues = objectDeDup(issues);
			for (j = 0; j < issues.length; j += 1) {
				sql += 'insert into commits_issues(commit,issue) values (?,?);'
				values.push(commit);
				values.push(parseInt(issues[j].substring(1)));
			}			
		}
		if (sql.length === 0) {
			coletaEntidades();
		} else {
			db.query(sql, values, function (err, result) {
				if (err) { throw err; }
				coletaEntidades();
			});			
		}
	});

	function coletaEntidades () {
		var cmd = 'git diff-tree --no-commit-id --name-only -r ' + commit;
		exec(cmd, {cwd:'../historage-data'}, function (err, stdout, stderr) {
			var lines = stdout.split('\n'), j;
			var line;
			for (j = 0; j < lines.length; j += 1) {
				line = lines[j].trim();
				if (line.indexOf('.f/') !== -1) {
					if (!mapaDeEntidades[line]) {
						entidades.push(line);
						mapaDeEntidades[line] = [];
					}
					mapaDeEntidades[line].push(commit);
				}
			}
			nextCommit(i + 1);
		});
	}

}

function proximaEntidade (i) {
	if (i >= entidades.length) {
		db.end();
		console.log('ok');
		return;
	}
	if (i % 100 === 0) {
		process.stdout.write('.');
	}
	var sql = 'insert into entidades(caminho,tipo) values (?,?)'; 
	db.query(sql, [entidades[i],tipoEntidade(entidades[i])], function (err, result) {
		if (err) { throw err; }
		proximoCommitEntidade(result.insertId, mapaDeEntidades[entidades[i]], 0);
	});

	function proximoCommitEntidade (entidadeId, commits, j) {
		if (j >= commits.length) {
			proximaEntidade(i+1);
			return;
		}
		var sql = 'insert into commits_entidades(commit, entidade) values (?, ?)'; 
		db.query(sql, [commits[j],entidadeId], function (err, result) {
			if (err) { throw err; }
			proximoCommitEntidade(entidadeId, commits, j+1);
		});
	}
}

function tipoEntidade (entidade) {
	var arr = entidade.split('/');
	if (arr.length < 2) return null;
	return arr[arr.length-2];
}

var objectDeDup = function(unordered) {
  var result = [];
  var object = {};
  unordered.forEach(function(item) {
    object[item] = null;
  });
  result = Object.keys(object);
  return result;
}