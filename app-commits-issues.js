var db = require('./db');

var commits;

db.query('select id, comentario from commits', function (err, result) {
	commits = result;
	nextCommit(0);
});

function nextCommit (i) {
	if (i >= commits.length) {
		db.end();
		return;
	}
	if (i % 100 === 0) {
		process.stdout.write('.');
	}
	
	var commit = commits[i].id;
	var issues = commits[i].comentario.match(/#(\d+)/g);

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
		nextCommit(i + 1);
	} else {
		db.query(sql, values, function (err, result) {
			if (err) { throw err; }
			nextCommit(i + 1);
		});			
	}

}

var objectDeDup = function(unordered) {
  var object = {};
  unordered.forEach(function(item) {
    object[item] = null;
  });
  return Object.keys(object);
}