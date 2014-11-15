var argv = require('optimist').argv;
var db = require('./db');

var repositoryName = argv._[0] || 'siop';

var source = argv._[1] || 'commits';

var MAX_ENTITIES = argv.max_entities || 100;

var repositoryMap = { 
	siop: 1, 
	derby: 2, 
	hadoop: 3, 
	wildfly: 4, 
	'eclipse.platform.ui': 5, 
	'eclipse.jdt': 6, 
	geronimo: 7, 
	lucene: 8 }

var repository = repositoryMap[repositoryName];

var sql = { 
	commits: '\
		select commit as id, entidade \
		from mpca.commits_entities \
		where commit in (select id from commits where repository = ?) \
		order by commit,entidade', 
	issues: '\
		select distinct issue as id, ce.commit, entidade \
		from mpca.commits_entities ce \
			inner join mpca.commits_issues ci on ci.commit = ce.commit \
		where ce.commit in \
			(select id from commits where repository = ?) \
		order by issue,entidade', 
	issues_only: '\
		select distinct issue as id, entidade \
		from mpca.commits_entities ce \
			inner join mpca.commits_issues ci on ci.commit = ce.commit \
		where ce.commit in \
			(select id from commits where repository = ?) \
		order by issue,entidade' }

var graph = {}

db.query(sql[source], [repository], function (err, result) {
	if (err) { throw err; }
	var entities = [];
	var previousId;
	var i;
	for (i = 0; i < result.length; i += 1) {
		if (result[i].id !== previousId) {
			collectCombinations(entities)
			entities = []
			previousId = result[i].id
		}
		entities.push(result[i].entidade)
	}
	db.end()
	collectCombinations(entities)
	var count = 0;
	Object.keys(graph).forEach(function (k) {
		var arr = k.split('|')
		if (graph[k] > 1) {
			console.log(arr[0] + ' ' + arr[1] + ' ' + graph[k])
		}
	});
});

function collectCombinations (entities) {
	if (entities.length > MAX_ENTITIES) { return }
	var i, j, key;
	for (i = 0; i < entities.length; i++) {
		for (j = 0; j < entities.length; j++) {
			if (entities[i] !== entities[j]) {
				key = entities[i] + '|' + entities[j]
				if (!graph[key]) {
					graph[key] = 0
				}
				graph[key] = graph[key] + 1
			}
		}
	}
}