var mysql = require('mysql');

var pool = mysql.createPool({
  host     : 'localhost',
  user     : 'root',
  password : '',
  database : 'mpca',
  multipleStatements: true
});

exports.query = function (sql, values, callback) {
	if (typeof callback === 'undefined') {
		callback = values;
		values = undefined;
	}
	pool.getConnection(function (err, connection) {
		if (err) { return callback(err); }
		var f = function (err, rows) {
			callback(err, rows);
			connection.release();
		};
		if (typeof values === 'undefined') {
			connection.query(sql, f);
		} else {
			connection.query(sql, values, f);
		}
	});
};

exports.end = function () {
	pool.end();
}