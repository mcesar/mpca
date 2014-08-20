var db = require('./db');

console.log('obtendo commits_entidades');

var grafo = {}

db.query('select * from mpca.commits_entidades order by commit', function (err, result) {
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
		if (i % 1000 == 0) {
			console.log(i + '***')
		}
	}
	console.log(i + '***')
	coletaCombinacoes(entidades)
	console.log(Object.keys(grafo).length + '<----------------')
});

function coletaCombinacoes (entidades) {
	if (entidades.length > 100) { return }
	console.log(entidades.length)
	var i, j, chave;
	for (i = 0; i < entidades.length; i++) {
		for (j = 0; j < entidades.length; j++) {
			if (entidades[i] !== entidades[j]) {
				chave = entidades[i] + '|' + entidades[j]
				if (grafo[chave]) {
					grafo[chave] = 0
				}
				grafo[chave] = grafo[chave] + 1
			}
		}
	}
}