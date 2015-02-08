#!/usr/local/bin/python3

import argparse
import xml.etree.ElementTree as etree
from db import Db
import constants
import re

repository_prefixes = { 
	'siop': {'xml':['br.gov','br.gov','br.gov'],'db':['SiopEJB/ejbModule/br/gov','SiopJPA/src/br/gov','SiopWAR/src/br/gov']}, 
	'derby': {'xml':['org.apache','org.apache','org.apache','org.apache','org.apache','org.apache','org.apache','org.apache'],'db':['java/build/org/apache','java/drda/org/apache','java/engine/org/apache','java/tools/org/apache','java/client/org/apache','java/shared/org/apache','java/storeless/org/apache','java/optional/org/apache']}, 
	'hadoop': {'xml':['org.apache','org.apache','org.apache','org.apache','org.apache','org.apache','org.apache','org.apache','org.apache','org.apache','org.apache','org.apache','org.apache','org.apache','org.apache','org.apache','org.apache','org.apache','org.apache','org.apache','org.apache','org.apache','org.apache','org.apache','org.apache','org.apache','org.apache','org.apache','org.apache','org.apache','org.apache','org.apache','org.apache','org.apache','org.apache','org.apache','org.apache','org.apache','org.apache','org.apache','org.apache'],'db':['hdfs/src/java/org/apache','hadoop-common/src/main/java/org/apache','hadoop-common-project/hadoop-annotations/src/main/java/org/apache','hadoop-common-project/hadoop-common/src/main/java/org/apache','hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache','hadoop-hdfs-project/hadoop-hdfs/src/ant/org/apache','hadoop-mapreduce-project/hadoop-mapreduce-client/hadoop-mapreduce-client-app/src/main/java/org/apache','hadoop-mapreduce-project/hadoop-mapreduce-client/hadoop-mapreduce-client-common/src/main/java/org/apache','hadoop-mapreduce-project/hadoop-mapreduce-client/hadoop-mapreduce-client-core/src/main/java/org/apache','hadoop-mapreduce-project/hadoop-mapreduce-client/hadoop-mapreduce-client-hs/src/main/java/org/apache','hadoop-mapreduce-project/hadoop-mapreduce-client/hadoop-mapreduce-client-jobclient/src/main/java/org/apache','hadoop-mapreduce-project/hadoop-mapreduce-client/hadoop-mapreduce-client-shuffle/src/main/java/org/apache','hadoop-common-project/hadoop-auth/src/main/java/org/apache','hadoop-tools/hadoop-streaming/src/main/java/org/apache','hadoop-hdfs-project/hadoop-hdfs-httpfs/src/main/java/org/apache','hadoop-tools/hadoop-archives/src/main/java/org/apache','hadoop-hdfs-project/hadoop-hdfs/src/contrib/bkjournal/src/main/java/org/apache','hadoop-tools/hadoop-extras/src/main/java/org/apache','hadoop-tools/hadoop-rumen/src/main/java/org/apache','hadoop-tools/hadoop-distcp/src/main/java/org/apache','hadoop-tools/hadoop-datajoin/src/main/java/org/apache','hadoop-tools/hadoop-gridmix/src/main/java/org/apache','hadoop-yarn-project/hadoop-yarn/hadoop-yarn-api/src/main/java/org/apache','hadoop-yarn-project/hadoop-yarn/hadoop-yarn-applications/hadoop-yarn-applications-distributedshell/src/main/java/org/apache','hadoop-yarn-project/hadoop-yarn/hadoop-yarn-applications/hadoop-yarn-applications-unmanaged-am-launcher/src/main/java/org/apache','hadoop-yarn-project/hadoop-yarn/hadoop-yarn-common/src/main/java','hadoop-yarn-project/hadoop-yarn/hadoop-yarn-server/hadoop-yarn-server-common/src/main/java/org/apache','hadoop-yarn-project/hadoop-yarn/hadoop-yarn-server/hadoop-yarn-server-nodemanager/src/main/java/org/apache','hadoop-yarn-project/hadoop-yarn/hadoop-yarn-server/hadoop-yarn-server-resourcemanager/src/main/java/org/apache','hadoop-yarn-project/hadoop-yarn/hadoop-yarn-server/hadoop-yarn-server-web-proxy/src/main/java/org/apache','hadoop-yarn-project/hadoop-yarn/hadoop-yarn-client/src/main/java/org/apache','hadoop-mapreduce-project/hadoop-mapreduce-client/hadoop-mapreduce-client-hs-plugins/src/main/java/org','hadoop-maven-plugins/src/main/java/org/apache','hadoop-common-project/hadoop-nfs/src/main/java/org/apache','hadoop-common-project/hadoop-minikdc/src/main/java/org/apache','hadoop-tools/hadoop-openstack/src/main/java/org/apache','hadoop-tools/hadoop-sls/src/main/java/org/apache','hadoop-yarn-project/hadoop-yarn/hadoop-yarn-server/hadoop-yarn-server-applicationhistoryservice/src/main/java/org/apache','hadoop-common-project/hadoop-kms/src/main/java/org/apache','hadoop-tools/hadoop-azure/src/main/java/org/apache','hadoop-tools/hadoop-aws/src/main/java/org/apache']}, 
	'wildfly': '', 
	'eclipse.platform.ui': {'xml':['org.eclipse','org.eclipse','org.eclipse','org.eclipse','org.eclipse','org.eclipse','org.eclipse','org.eclipse','org.eclipse','org.eclipse','org.eclipse','org.eclipse','org.eclipse','org.eclipse','org.eclipse','org.eclipse','org.eclipse','org.eclipse','org.eclipse','org.eclipse','org.eclipse','org.eclipse','org.eclipse','org.eclipse','org.eclipse','org.eclipse','org.eclipse','org.eclipse','org.eclipse','org.eclipse','org.eclipse','org.eclipse','org.eclipse','org.eclipse','org.eclipse','org.eclipse','org.eclipse','org.eclipse','org.eclipse','org.eclipse','org.eclipse','org.eclipse','org.eclipse'],'db':['bundles/org.eclipse.jface/src/org/eclipse','bundles/org.eclipse.ui.win32/src/org/eclipse','bundles/org.eclipse.ui.views/src/org/eclipse','bundles/org.eclipse.ui.workbench/Eclipse UI Editor Support/org/eclipse','bundles/org.eclipse.ui.workbench/Eclipse UI/org/eclipse','bundles/org.eclipse.ui/src/org/eclipse/ui','bundles/org.eclipse.ui.ide/src/org/eclipse','bundles/org.eclipse.ui.ide/extensions/org/eclipse','bundles/org.eclipse.ui.workbench.compatibility/src/org/eclipse','bundles/org.eclipse.ui.forms/src/org/eclipse','bundles/org.eclipse.ui.presentations.r21/src/org/eclipse','bundles/org.eclipse.core.commands/src/org/eclipse','bundles/org.eclipse.ui.navigator/src/org/eclipse','bundles/org.eclipse.ui.browser/src/org/eclipse','bundles/org.eclipse.jface.databinding/src/org/eclipse','bundles/org.eclipse.ui.views.properties.tabbed/src/org/eclipse','bundles/org.eclipse.ui.navigator.resources/src/org/eclipse','bundles/org.eclipse.core.databinding.beans/src/org/eclipse','bundles/org.eclipse.core.databinding/src/org/eclipse','bundles/org.eclipse.core.databinding.observable/src/org/eclipse','bundles/org.eclipse.ui.ide.application/src/org/eclipse','bundles/org.eclipse.ui.cocoa/src/org/eclipse/ui','bundles/org.eclipse.e4.ui.model.workbench/src/org/eclipse','bundles/org.eclipse.e4.ui.css.core/src/org/eclipse','bundles/org.eclipse.e4.ui.css.swt/src/org/eclipse','bundles/org.eclipse.core.databinding.property/src/org/eclipse','bundles/org.eclipse.e4.ui.services/src/org/eclipse','bundles/org.eclipse.e4.ui.workbench.swt/src/org/eclipse','bundles/org.eclipse.e4.core.commands/src/org/eclipse','bundles/org.eclipse.e4.ui.bindings/src/org/eclipse','bundles/org.eclipse.ui.carbon/src/org/eclipse','bundles/org.eclipse.e4.ui.workbench3/src/org/eclipse','bundles/org.eclipse.e4.ui.workbench/src/org/eclipse','bundles/org.eclipse.e4.ui.workbench.addons.swt/src/org/eclipse','bundles/org.eclipse.e4.ui.css.swt.theme/src/org/eclipse','bundles/org.eclipse.e4.ui.di/src/org/eclipse','bundles/org.eclipse.e4.ui.workbench.renderers.swt/src/org/eclipse','bundles/org.eclipse.e4.ui.workbench.renderers.swt.cocoa/src/org/eclipse','bundles/org.eclipse.e4.emf.xpath/src/org/eclipse','bundles/org.eclipse.e4.ui.widgets/src/org/eclipse','bundles/org.eclipse.ui.images.renderer/src/main/java/org/eclipse','bundles/org.eclipse.e4.ui.progress/src/org/eclipse','bundles/org.eclipse.ui.monitoring/src/org/eclipse']}, 
	'eclipse.jdt': {'xml':['org.eclipse','org.eclipse','org.eclipse','org.eclipse','org.eclipse','org.eclipse','org.eclipse','org.eclipse','org.eclipse','org.eclipse','org.eclipse','org.eclipse','com.sun','org.eclipse','org.eclipse','org.eclipse','org.eclipse'],'db':['org.eclipse.jdt.core/batch/org/eclipse','org.eclipse.jdt.core/codeassist/org/eclipse','org.eclipse.jdt.core/compiler/org/eclipse','org.eclipse.jdt.core/eval/org/eclipse','org.eclipse.jdt.core/model/org/eclipse','org.eclipse.jdt.core/search/org/eclipse','org.eclipse.jdt.core/dom/org/eclipse','org.eclipse.jdt.core/antadapter/org/eclipse','org.eclipse.jdt.core.tests.model/src/org/eclipse','org.eclipse.jdt.core/formatter/org/eclipse','org.eclipse.jdt.apt.core/src/org/eclipse','org.eclipse.jdt.apt.ui/src/org/eclipse','org.eclipse.jdt.apt.core/src/com/sun','org.eclipse.jdt.compiler.tool/src/org/eclipse','org.eclipse.jdt.compiler.apt/src/org/eclipse','org.eclipse.jdt.apt.pluggable.core/src/org/eclipse','org.eclipse.jdt.annotation/src/org/eclipse']}, 
	'geronimo': {'xml':['org.apache','org.apache','org.apache','org.apache','org.apache','org.apache','org.apache','org.apache','org.apache','org.apache','org.apache','org.apache','org.apache','org.apache','org.apache','org.apache','org.apache','org.apache','org.apache','org.apache','org.apache','org.apache','org.apache','org.apache','org.apache','org.apache','org.apache','org.apache','org.apache','org.apache','org.apache','org.apache','org.apache','org.apache','org.apache','org.apache','org.apache','org.apache','org.apache','org.apache','org.apache','org.apache','org.apache','org.apache','org.apache','org.apache','org.apache','org.apache','org.apache','org.apache','org.apache','org.apache','org.apache','org.apache','org.apache','org.apache','org.apache','org.apache','org.apache','org.apache','org.apache','org.apache','org.apache','org.apache','org.apache','org.apache','org.apache','org.apache','org.apache','org.apache','org.apache','org.apache','org.apache','org.apache','org.apache','org.apache','org.apache','org.apache','org.apache','org.apache','org.apache','org.apache','org.apache','org.apache','org.apache','org.apache','org.apache','org.apache','org.apache','org.apache','org.apache','org.apache','org.apache','org.apache','org.apache','org.apache','org.apache','org.apache','org.apache','org.apache','org.apache','org.apache','org.apache','org.apache','org.apache','org.apache','org.apache','org.apache','org.apache','org.apache','org.apache','org.apache','org.apache','org.apache','org.apache','org.apache','org.apache','org.apache','org.apache','org.apache','org.apache','org.apache','org.apache','org.apache','org.apache','org.apache','org.apache','org.apache','org.apache','org.apache','org.apache','org.apache','org.apache'],'db':['plugins/console/console-base-portlets/src/main/java/org/apache','plugins/console/console-core/src/main/java/org/apache','plugins/debugviews/debugviews-portlets/src/main/java/org/apache','plugins/plancreator/plancreator-portlets/src/main/java/org/apache','plugins/pluto/geronimo-pluto/src/main/java/org/apache','plugins/axis/geronimo-axis/src/main/java/org/apache','plugins/axis/geronimo-axis-builder/src/main/java/org/apache','plugins/axis2/geronimo-axis2/src/main/java/org/apache','plugins/axis2/geronimo-axis2-builder/src/main/java/org/apache','plugins/axis2/geronimo-axis2-ejb/src/main/java/org/apache','plugins/client/geronimo-client/src/main/java/org/apache','plugins/client/geronimo-client-builder/src/main/java/org/apache','plugins/clustering/geronimo-clustering/src/main/java/org/apache','plugins/clustering/geronimo-clustering-wadi/src/main/java/org/apache','plugins/corba/geronimo-corba/src/main/java/org/apache','plugins/corba/geronimo-corba-builder/src/main/java/org/apache','plugins/cxf/geronimo-cxf/src/main/java/org/apache','plugins/cxf/geronimo-cxf-builder/src/main/java/org/apache','plugins/cxf/geronimo-cxf-ejb/src/main/java/org/apache/geronimo','plugins/j2ee/geronimo-j2ee-builder/src/main/java/org/apache','plugins/j2ee/geronimo-j2ee-schema/src/main/java/org/apache','plugins/jasper/geronimo-jasper/src/main/java/org/apache','plugins/jasper/geronimo-jasper-builder/src/main/java/org/apache','plugins/jaxws/geronimo-jaxws-builder/src/main/java/org/apache','plugins/myfaces/geronimo-myfaces/src/main/java/org/apache','plugins/myfaces/geronimo-myfaces-builder/src/main/java/org/apache','plugins/openejb/geronimo-openejb/src/main/java/org/apache','plugins/openejb/geronimo-openejb-builder/src/main/java/org/apache','plugins/webservices/geronimo-webservices/src/main/java/org/apache','plugins/webservices/geronimo-webservices-builder/src/main/java/org/apache','plugins/corba/geronimo-yoko/src/main/java/org/apache','plugins/hotdeploy/geronimo-hot-deploy/src/main/java/org/apache','plugins/j2ee/geronimo-naming-builder/src/main/java/org/apache','plugins/j2ee/geronimo-security-builder/src/main/java/org/apache','plugins/j2ee/geronimo-web-2.5-builder/src/main/java/org/apache','plugins/j2ee/geronimo-test-ddbean/src/main/java/org/apache','plugins/system-database/geronimo-derby/src/main/java/org/apache','plugins/console/geronimo-converter/src/main/java/org/apache','plugins/console/plugin-portlets/src/main/java/org/apache','plugins/system-database/sysdb-portlets/src/main/java/org/apache','plugins/clustering/geronimo-farm/src/main/java/org/apache','plugins/ca-helper/geronimo-ca-helper/src/main/java/org/apache','plugins/mejb/geronimo-mejb/src/main/java/org/apache','plugins/monitoring/agent-jar/src/main/java/org/apache','plugins/monitoring/mconsole-war/src/main/java/org','plugins/remote-deploy/geronimo-remote-deploy/src/main/java/org/apache','plugins/welcome/geronimo-welcome/src/main/java/org/apache','plugins/openejb/geronimo-openejb-clustering-builder-wadi/src/main/java/org/apache','plugins/openejb/geronimo-openejb-clustering-wadi/src/main/java/org/apache','plugins/aspectj/geronimo-aspectj/src/main/java/org/apache','plugins/clustering/geronimo-deploy-farm/src/main/java/org/apache','plugins/clustering/geronimo-plugin-farm/src/main/java/org/apache','plugins/j2ee/geronimo-j2ee/src/main/java/org/apache','plugins/connector-1_6/geronimo-connector-builder-1_6/src/main/java/org/apache','plugins/openejb/openejb-portlets/src/main/java/org/apache','plugins/monitoring/agent-jmx/src/main/java/org/apache','plugins/cxf/geronimo-cxf-tools/src/main/java/org/apache','plugins/activemq/activemq-portlets/src/main/java/org/apache','plugins/console/console-filter/src/main/java/org/apache','plugins/console/console-portal-driver/src/main/java/org/apache','plugins/openwebbeans/geronimo-openwebbeans-builder/src/main/java/org/apache','plugins/openjpa2/geronimo-openjpa2/src/main/java/org/apache','plugins/openjpa2/geronimo-persistence-jpa20/src/main/java/org/apache','plugins/openjpa2/geronimo-persistence-jpa20-builder/src/main/java/org/apache','framework/buildsupport/car-maven-plugin/src/main/java/org/apache','framework/buildsupport/geronimo-maven-plugin/src/main/java/org/apache','framework/buildsupport/testsuite-maven-plugin/src/main/java/org/apache','framework/modules/geronimo-cli/src/main/java/org/apache','framework/modules/geronimo-common/src/main/java/org/apache','framework/modules/geronimo-config-groovy-transformer/src/main/java/org/apache','framework/modules/geronimo-core/src/main/java/org/apache','framework/modules/geronimo-crypto/src/main/java/org/apache','framework/modules/geronimo-deploy-config/src/main/java/org/apache','framework/modules/geronimo-deploy-jsr88/src/main/java/org/apache','framework/modules/geronimo-deploy-tool/src/main/java/org/apache','framework/buildsupport/geronimo-osgi-plugin/src/main/java/org/apache','framework/buildsupport/geronimo-property-plugin/src/main/java/org/apache','framework/modules/geronimo-blueprint/src/main/java/org/apache','framework/modules/geronimo-bundle-recorder/src/main/java/org/apache','framework/modules/geronimo-deploy-jsr88-full/src/main/java/org/apache','framework/modules/geronimo-deploy-tool/src/main/java/org/apache','framework/modules/geronimo-deployment/src/main/java/org/apache','framework/modules/geronimo-hook/src/main/java/org/apache','framework/modules/geronimo-interceptor/src/main/java/org/apache','framework/modules/geronimo-jdbc/src/main/java/org/apache','framework/modules/geronimo-jmx-remoting/src/main/java/org/apache','framework/modules/geronimo-kernel/src/main/java/org/apache','framework/modules/geronimo-main/src/main/java/org/apache','framework/modules/geronimo-management/src/main/java/org/apache','framework/modules/geronimo-naming/src/main/java/org/apache','framework/modules/geronimo-obr/src/main/java/org/apache','framework/modules/geronimo-pax-logging/src/main/java/org/apache','framework/modules/geronimo-plugin/src/main/java/org/apache','framework/modules/geronimo-rmi-loader/src/main/java/org/apache','framework/modules/geronimo-security/src/main/java/org/apache','framework/modules/geronimo-service-builder/src/main/java/org/apache','framework/modules/geronimo-shell-base/src/main/java/org/apache','framework/modules/geronimo-shell-diagnose/src/main/java/org/apache','framework/modules/geronimo-system/src/main/java/org/apache','framework/modules/geronimo-transformer/src/main/java/org/apache','framework/modules/testsupport-common/src/main/java/org/apache','plugins/activemq/geronimo-activemq-blueprint/src/main/java/org/apache','plugins/activemq/geronimo-activemq-management/src/main/java/org/apache','plugins/aries/geronimo-aries-builder/src/main/java/org/apache','plugins/aries/geronimo-aries-shell/src/main/java/org/apache','plugins/aries/geronimo-aries/src/main/java/org/apache','plugins/axis2/geronimo-axis2-ejb-builder/src/main/java/org/apache','plugins/bval/geronimo-bval-builder/src/main/java/org/apache','plugins/bval/geronimo-bval/src/main/java/org/apache','plugins/connector-1_6/geronimo-connector-1_6/src/main/java/org/apache','plugins/connector-1_6/geronimo-transaction-1_6/src/main/java/org/apache','plugins/cxf/geronimo-cxf-ejb-builder/src/main/java/org/apache','plugins/j2ee/geronimo-web/src/main/java/org/apache','plugins/javamail/geronimo-mail/src/main/java/org/apache','plugins/jaxws/geronimo-jaxws-ejb-builder/src/main/java/org/apache','plugins/jaxws/geronimo-jaxws-sun-tools/src/main/java/org/apache','plugins/jetty8/geronimo-jetty8-builder/src/main/java/org/apache','plugins/jetty8/geronimo-jetty8-clustering-builder-wadi/src/main/java/org/apache','plugins/jetty8/geronimo-jetty8-clustering-wadi/src/main/java/org/apache','plugins/jetty8/geronimo-jetty8/src/main/java/org/apache','plugins/monitoring/agent-ejb/src/main/java/org/apache','plugins/openjpa2/geronimo-aries-jpa/src/main/java/org/apache','plugins/openwebbeans/geronimo-openwebbeans/src/main/java/org/apache','plugins/sharedlib/geronimo-sharedlib/src/main/java/org/apache','plugins/tomcat/geronimo-tomcat7-builder/src/main/java/org/apache','plugins/tomcat/geronimo-tomcat7-clustering-builder-wadi/src/main/java/org/apache','plugins/tomcat/geronimo-tomcat7-clustering-wadi/src/main/java/org/apache','plugins/tomcat/geronimo-tomcat7/src/main/java/org/apache','plugins/uddi/uddi-war-repackage/src/main/java/org/apache','plugins/wab/geronimo-wab/src/main/java/org/apache','plugins/wab/geronimo-web-extender/src/main/java/org/apache','plugins/wink/geronimo-wink-builder/src/main/java/org/apache','plugins/wink/geronimo-wink/src/main/java/org/apache']}, 
	'lucene': {'xml':['org.apache','org.apache','org.apache','org.tartarus','org.apache','org.apache','org.apache','org.apache','org.apache','org.apache','org.apache','org.apache','org.egothor','org.apache','org.apache','org.apache','org.apache','org.apache','org.apache','org.apache','org.apache','org.apache','org.apache','org.apache','org.apache','org.apache','org.apache','org.apache','org.apache','org.apache','org.apache','org.apache'],'db':['lucene/core/src/java/org/apache','lucene/tools/src/java/org','lucene/analysis/common/src/java/org/apache','lucene/analysis/common/src/java/org/tartarus','lucene/analysis/icu/src/java/org/apache','lucene/analysis/icu/src/tools/java/org/apache/lucene','lucene/analysis/kuromoji/src/java/org/apache','lucene/analysis/kuromoji/src/tools/java/org/apache','lucene/analysis/morfologik/src/java/org/apache','lucene/analysis/phonetic/src/java/org/apache','lucene/analysis/smartcn/src/java/org/apache','lucene/analysis/stempel/src/java/org/apache','lucene/analysis/stempel/src/java/org/egothor','lucene/analysis/uima/src/java/org/apache','lucene/benchmark/src/java/org/apache','lucene/demo/src/java/org/apache','lucene/facet/src/java/org/apache','lucene/grouping/src/java/org/apache','lucene/highlighter/src/java/org/apache','lucene/join/src/java/org/apache','lucene/memory/src/java/org/apache','lucene/misc/src/java/org/apache','lucene/queries/src/java/org/apache','lucene/queryparser/src/java/org/apache','lucene/sandbox/src/java/org/apache','lucene/spatial/src/java/org/apache','lucene/suggest/src/java/org/apache','lucene/codecs/src/java/org/apache','lucene/classification/src/java/org/apache','lucene/replicator/src/java/org/apache','lucene/expressions/src/java/org/apache','lucene/test-framework/src/java/org/apache']}, 
	'jhotdraw7': {'xml':['org.jhotdraw'],'db':['src/main/java/org/jhotdraw']} }

def load_entities_from_db():
	db = Db()
	repository_id = constants.repository_map[args.repository]
	prefixes = repository_prefixes[args.repository]['db']
	db_entities = {}
	sql_args = (repository_id,)
	prefixes_str = ''
	for prefix in prefixes:
		sql_args += (prefix + '%',)
		if len(prefixes_str) > 0: prefixes_str += ' or '
		prefixes_str += 'caminho like %s'
	cursor = db.query(
		"select id, caminho from entidades where repositorio = %s and (" + prefixes_str + ")", sql_args)
	for (id, path) in cursor:
		key = to_java_convention(path, args.repository, True)
		if not key in db_entities: db_entities[key] = {'id': id, 'path': path}
	db.close()
	return db_entities

def load_evolutionary_dependencies_from_db():
	db = Db()
	repository_id = constants.repository_map[args.repository]
	types = 'CN,CM,FE,MT'
	if args.coarse_grained:
		types = 'CL,IN'
	graphs_ed = {}
	cursor = db.query("""select g.id, g.source, g.max_entities, g.min_confidence, 
			g.min_support, g.min_date, g.types, de.entidade1, de.entidade2, e.caminho
		from dependencias_evolucionarias de 
			inner join grafos_de g on de.grafo = g.id 
			inner join entidades e on de.entidade2 = e.id 
		where g.repositorio = %s and g.types = %s""", 
		(repository_id,types))
	for (id, source, max_entitites, min_confidence, min_support, min_date, types, entity1, entity2, e2_path) in cursor:
		if id not in graphs_ed:
			graphs_ed[id] = {
				'source': source, 
				'max_entitites': max_entitites, 
				'min_confidence': min_confidence, 
				'min_support': min_support, 
				'min_date': min_date, 
				'types': types,
				'dependencies': {}
			}
		if entity1 not in graphs_ed[id]['dependencies']:
			graphs_ed[id]['dependencies'][entity1] = []
		entity2_java_name = to_java_convention(e2_path, args.repository, True)
		graphs_ed[id]['dependencies'][entity1].append(entity2_java_name)
	db.close()
	return graphs_ed

def to_java_convention(path, repository, strip_generics=False):
	arr = path.split('/')
	new_arr = []
	class_count = 0
	for s in arr:
		if s.endswith('.f'):
			continue
		if s == 'CL':
			class_count += 1
			if class_count > 1:
				s = '$'
		if s in constants.entity_types:
			continue
		new_s = re.sub('\.c$', '', s)
		# remove generic types
		if strip_generics:
			while '<' in new_s:
				i = new_s.find('<')
				count = 0
				for j in range(i, len(new_s)):
					if new_s[j] == '>':
						count -= 1
					if new_s[j] == '<':
						count += 1
					if count == 0:
						break
				new_s = new_s.replace(new_s[i:j+1], '')
		# change signature of inner classe's constructors
		if '(' in new_s and class_count > 1 and new_s.partition('(')[0] == new_arr[len(new_arr)-1]:
			outer_class = new_arr[len(new_arr)-3]
			new_s = outer_class + '$' + new_s
			if '()' in new_s:
				new_s = new_s.replace('(', '(' + outer_class)
			#else:
			#	new_s = new_s.replace('(', '(' + outer_class + ',')
		new_arr.append(new_s)
	result = '.'.join(new_arr).replace('.$.','$')
	for i in range(0, len(repository_prefixes[repository]['db'])):
		prefix_db = repository_prefixes[repository]['db'][i].replace('/', '.')
		prefix_xml = repository_prefixes[repository]['xml'][i]
		result = result.replace(prefix_db, prefix_xml)
	return result

def parse_xml():
	"""Parse XML from DependencyFinder"""
	root = etree.parse(args.file).getroot()
	prefixes = repository_prefixes[args.repository]['xml']
	classes = {}
	for e1 in root:
		for e2 in e1:
			if e2.tag == 'name':
				package_name = e2.text
				if package_name is None: package_name = ''
			has_prefix = [prefix for prefix in prefixes if package_name.startswith(prefix)]
			if e2.tag == 'class' and has_prefix and e2.attrib['confirmed'] == 'yes':
				is_enum = False
				for e3 in e2:
					if e3.tag == 'name':
						class_dict = {'name': e3.text, 'entities': [], 'superclasses': [], 'dependencies': set()}
						classes[e3.text] = class_dict
					if e3.tag == 'outbound' and e3.attrib['type'] == 'class' and e3.attrib['confirmed'] == 'no' and e3.text == 'java.lang.Enum':
						is_enum = True
					elif e3.tag == 'outbound' and e3.attrib['type'] == 'class' and e3.attrib['confirmed'] == 'yes':
						class_dict['superclasses'].append(e3.text)
					if e3.tag == 'feature' and e3.attrib['confirmed'] == 'yes':
						for e4 in e3:
							if e4.tag == 'name':
								feature_name = simplified_args(e4.text)
								# ignores static initializers
								if simple_name(feature_name) == 'static {}':
									break
								# ignores enum features not supported by historage
								if is_enum and simple_name(feature_name) in ['$VALUES', 'valueOf', 'values']:
									break
								# find out the feature type
								if feature_name.endswith(')'):
									if simple_name(feature_name) == simple_name(class_dict['name']):
										feature_type = 'CN'
									else:
										feature_type = 'MT'
								else:
									feature_type = 'FE'
								# ignores enums constructors
								if is_enum and feature_type == 'CN' and feature_name.endswith(simple_name(feature_name) + '(String,int)'):
									break
								feature_dict = {'name': feature_name, 'dependencies': []}
								class_dict['entities'].append(feature_dict)
								feature_dict['type'] = feature_type
							has_prefix = [prefix for prefix in prefixes if e4.text.startswith(prefix)]
							if e4.tag == 'outbound' and has_prefix and e4.attrib['type'] == 'feature':
								#e4.attrib['confirmed'] == 'yes' and
								dependency_name = simplified_args(e4.text)
								#if class_top_level_name(feature_name) != class_top_level_name(dependency_name):
								feature_dict['dependencies'].append(dependency_name)
								if class_dict['name'] != class_name(dependency_name):
									class_dict['dependencies'].add(class_name(dependency_name))
	return classes

def class_name(feature_name):
	result = feature_name
	if result.find('(') != -1:
		result = result[:result.find('(')]
	result = result[:result.rfind('.')]
	return result

def class_top_level_name(feature_name):
	result = class_name(feature_name)
	if result.find('$') != -1:
		result = result[:result.find('$')]
	return result

def simplified_args(feature_name):
	if not '(' in feature_name: return feature_name
	args_str = feature_name[feature_name.find('(')+1:len(feature_name)-1]
	args = args_str.split(',')
	new_args = []
	for arg in args:
		simple_arg = simple_name(arg)
		simple_arg = simple_arg.rpartition('$')[2]
		new_args.append(simple_arg)
	return feature_name.replace('('+args_str+')','(' + ','.join(new_args) + ')')

def simple_name(qualified_name):
	result = qualified_name
	if result.find('(') != -1:
		result = result[:result.find('(')]
	result = result[result.rfind('.')+1:]
	return result.strip()

def is_default_constructor(feature_name):
	class_name = simple_name(feature_name.rpartition('.')[0])
	if simple_name(feature_name) != class_name:
		return False
	if feature_name.endswith('()'):
		return True
	if '$' in class_name:
		return feature_name.endswith("({})".format(class_name.partition('$')[0]))	

def find_id_in_class_or_superclasses(feature_name, classes, db_entities, e):
	#cn = class_name(feature_name)
	#superclasses = classes[cn]['superclasses']
	if feature_name not in db_entities:
		# anonymous_inner_class = re.search('\$\d+\.', feature_name)
		# compiler_generated_element = re.search('access\$\d+\(', feature_name) or re.search('\.this\$\d+', feature_name)
		# default_constructor = is_default_constructor(feature_name)
		# # prints feature names not found in db
		# if anonymous_inner_class and not compiler_generated_element and not default_constructor:
		# 	print(feature_name)
		return None
	return db_entities[feature_name]['id']

def import_static_dependencies(db_entities, classes, coarse_grained):
	db = Db()

	table_suffix = ""
	if coarse_grained:
		table_suffix = "_coarse_grained"

	if not args.dont_store:
		db.delete("""
			delete from dependencias{} 
			where entidade1 in (select id from entidades where repositorio=%s)""".format(table_suffix),
			(constants.repository_map[args.repository],))

	dep_map = {}

	for c in classes.values():
		if coarse_grained:
			if c['name'] in db_entities:
				caller_id = db_entities[c['name']]['id']
				for d in c['dependencies']:
					if d in db_entities and not args.dont_store:
						calle_id = db_entities[d]['id']
						db.insert('insert into dependencias_coarse_grained values (%s,%s)', (caller_id, calle_id))
				if args.verbose and not args.not_found:
					print(c['name'])
			else:
				anonymous_inner_class = re.search('\$\d+$', c['name'])
				if args.verbose and args.not_found and not anonymous_inner_class:
					print(c['name'])
		else:
			for e in c['entities']:
				if e['name'] in db_entities:
					caller_id = db_entities[e['name']]['id']
					for d in e['dependencies']:
						calle_id = find_id_in_class_or_superclasses(d, classes, db_entities, e)
						if calle_id:
							#print(db_entities[e['name']]['id'], db_entities[d]['id'])
							if not args.dont_store and '{}-{}'.format(caller_id, calle_id) not in dep_map:
								db.insert('insert into dependencias values (%s,%s)', (caller_id, calle_id))
								dep_map['{}-{}'.format(caller_id, calle_id)] = True
						#else:
						#	if args.verbose: print(d)
					if args.verbose and not args.not_found:
						print(e['name'])
				else:
					# ignore entities not supported by historage
					anonymous_inner_class = re.search('\$\d+\.', e['name'])
					compiler_generated_element = re.search('access\$\d+\(', e['name']) or re.search('\.this\$\d+', e['name'])
					default_constructor = is_default_constructor(e['name'])
					# prints feature names not found in db
					if args.verbose and args.not_found and not anonymous_inner_class and not compiler_generated_element and not default_constructor:
					 	print(e['name'])

	db.commit()
	db.close()

def export_evolutionary_dependencies(db_entities, classes, e_graphs, repository):
	for g in e_graphs.values():
		if g['types'] == 'CL,IN':
			grain = 'coarse_grained'
		else:
			grain = 'fine_grained'
		file_name = 'mixed-dependencies_{}_{}_n{}_c{}_s{}_d{}_{}.ldi'.format(repository,g['source'],g['max_entitites'],str(g['min_confidence']).replace('.','_'),g['min_support'],g['min_date'],grain)
		prefixes = repository_prefixes[args.repository]['xml']
		with open(file_name, 'w') as f:
			print(file_name)
			f.write('<?xml version=\"1.0\" ?>\n<ldi>\n')
			class_count = 0
			for c in classes.values():
				has_prefix = [prefix for prefix in prefixes if c['name'].startswith(prefix)]
				if not has_prefix:
					continue
				class_count += 1
				if grain == 'coarse_grained':
					f.write("    <element name=\"{}\">\n".format(c['name']))
					for d in c['dependencies']:
						has_prefix = [prefix for prefix in prefixes if d.startswith(prefix)]
						if not has_prefix:
							continue
						f.write("        <uses provider=\"{}\" kind=\"static\"/>\n".format(d))
					if c['name'] in db_entities:
						entity_id = db_entities[c['name']]['id']
						write_evol_deps_of_entity(f, entity_id, g)
					f.write("    </element>\n")
				else:
					for e in c['entities']:
						f.write("    <element name=\"{}\">\n".format(e['name']))
						for d in e['dependencies']:
							f.write("        <uses provider=\"{}\" kind=\"static\"/>\n".format(d))
						if e['name'] in db_entities:
							entity_id = db_entities[e['name']]['id']
							write_evol_deps_of_entity(f, entity_id, g)
						f.write("    </element>\n")
			f.write('</ldi>')
			print(class_count)

def write_evol_deps_of_entity(f, entity_id, g):
	prefixes = repository_prefixes[args.repository]['xml']
	if entity_id in g['dependencies']:
		evol_deps = g['dependencies'][entity_id]
		for e_d in evol_deps:
			has_prefix = [prefix for prefix in prefixes if e_d.startswith(prefix)]
			if not has_prefix:
				continue
			f.write("        <uses provider=\"{}\" kind=\"evolutionary\"/>\n".format(e_d))

if __name__ == '__main__':

	parser = argparse.ArgumentParser()
	parser.add_argument("-f", "--file")
	parser.add_argument("-r", "--repository")
	parser.add_argument("-d", "--dont_store", action="store_true", default=False)
	parser.add_argument("-v", "--verbose", action="store_true")
	parser.add_argument("-n", "--not_found", action="store_true")
	parser.add_argument("-e", "--evolutionary_dependencies", action="store_true", default=False)
	parser.add_argument("-c", "--coarse_grained", action="store_true", default=False)
	args = parser.parse_args()

	db_entities = load_entities_from_db()
	classes = parse_xml()

	if args.evolutionary_dependencies:
		e_graphs = load_evolutionary_dependencies_from_db()
		export_evolutionary_dependencies(db_entities, classes, e_graphs, args.repository)
	else:
		import_static_dependencies(db_entities, classes, args.coarse_grained)

	# print('org.apache.lucene.codecs.asserting.AssertingDocValuesFormat$AssertingDocValuesConsumer.in')
	# print(to_java_convention('lucene/test-framework/src/java/org/apache/lucene/analysis/CannedBinaryTokenStream.f/CL/CannedBinaryTokenStream.c/CL/BinaryTermAttributeImpl.c/FE/bytes', args.repository))