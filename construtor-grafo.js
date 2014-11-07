var argv = require('optimist').argv;
var db = require('./db');

var repositorioName = argv._[0] || 'siop';

var repositorioMap = { siop: 1, derby: 2, hadoop: 3, wildfly: 4, 'eclipse.platform.ui': 5, 'eclipse.jdt': 6, 'geronimo': 7, 'lucene': 8 }

var repositorio = repositorioMap[repositorioName];

var grafo = {}

db.query('select * from mpca.commits_entidades where commit in (select id from commits where repositorio = ' + repositorio + ') order by commit,entidade', function (err, result) {
	if (err) { throw err; }
	var entidades = [];
	var commitAnterior;
	var i;
	for (i = 0; i < result.length; i += 1) {
		if (result[i].commit !== commitAnterior) {
			coletaCombinacoes(entidades)
			entidades = []
			commitAnterior = result[i].commit
		}
		entidades.push(result[i].entidade)
	}
	db.end()
	coletaCombinacoes(entidades)
	var count = 0;
	Object.keys(grafo).forEach(function(k) {
		var arr = k.split('|')
		if (grafo[k] > 1) {
			console.log(arr[0] + ' ' + arr[1] + ' ' + grafo[k])
		}
	});
});

function coletaCombinacoes (entidades) {
	if (entidades.length > 100) { return }
	var i, j, chave;
	for (i = 0; i < entidades.length; i++) {
		for (j = 0; j < entidades.length; j++) {
			if (entidades[i] !== entidades[j]) {
				chave = entidades[i] + '|' + entidades[j]
				if (!grafo[chave]) {
					grafo[chave] = 0
				}
				grafo[chave] = grafo[chave] + 1
			}
		}
	}
}