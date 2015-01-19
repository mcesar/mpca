var argv = require('optimist').argv;
var db = require('./db');

var repositoryName = argv._[0] || 'siop';

var source = argv._[1] || 'commits';

var MAX_ENTITIES = argv.max_entities || 100;

var MIN_WEIGHT = argv.min_weight || 2;

var MIN_DATE = argv.min_date || '1900-01-01';

var TYPES = argv.types || 'CL,CN,CM,FE,IN,MT';

var repositoryMap = { 
	siop: 1, 
	derby: 2, 
	hadoop: 3, 
	wildfly: 4, 
	'eclipse.platform.ui': 5, 
	'eclipse.jdt': 6, 
	geronimo: 7, 
	lucene: 8,
	'jhotdraw7': 9 }

var repository = repositoryMap[repositoryName];

var sql = { 
	commits: '\
		select commit as id, entidade \
		from mpca.commits_entidades ce \
			inner join mpca.entidades e on ce.entidade = e.id \
		where commit in (select id from commits where repositorio = ? and data >= ?) \
			and e.tipo in (?in?) \
		order by commit,entidade', 
	issues: '\
		select distinct issue as id, ce.commit, entidade \
		from mpca.commits_entidades ce \
			inner join mpca.commits_issues ci on ci.commit = ce.commit \
			inner join mpca.entidades e on ce.entidade = e.id \
		where ce.commit in \
			(select id from commits where repositorio = ? and data >= ?) \
			and e.tipo in (?in?) \
		order by issue,entidade', 
	issues_only: '\
		select distinct issue as id, entidade \
		from mpca.commits_entidades ce \
			inner join mpca.commits_issues ci on ci.commit = ce.commit \
			inner join mpca.entidades e on ce.entidade = e.id \
		where ce.commit in \
			(select id from commits where repositorio = ? and data >= ?) \
			and e.tipo in (?in?) \
		order by issue,entidade' }

var graph = {};

var actual_sql = sql[source];
var types_arr = TYPES.split(',');
var in_str = ''
var sql_params = [repository, MIN_DATE];

for (var i = 0; i < types_arr.length; i++) {
	if (i > 0) in_str += ',';
	in_str += '?';
	sql_params.push(types_arr[i]);
}

actual_sql = actual_sql.replace('?in?', in_str);

db.query(actual_sql, sql_params, function (err, result) {
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
		if (graph[k] >= MIN_WEIGHT) {
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