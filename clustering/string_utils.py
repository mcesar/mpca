def has_prefix(str, prefixes):
	return len([prefix for prefix in prefixes if str.startswith(prefix)]) > 0