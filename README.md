# Pesquisa-cientifica

Documentação para configurar e rodar as seguintes ferramentas de merge:

-FSTMerge
-AutoMerge
-JDime
-KDiff

Para rodar o FSTMerge, temos que apenas executar o arquivo .jar:

para rodar FSTMerge exemplo: java -jar ./FSTMerge/featurehouse_20220107.jar --expression /workspaces/Pesquisa-cientifica/senarios_merge_base/FSTMerge/scenario_1/merge.expression --base-directory /workspaces/Pesquisa-cientifica/senarios_merge_base/FSTMerge/scenario_1

versão antiga - (java -jar ./FSTMerge/featurehouse_20220107.jar --expression /workspaces/Pesquisa-cientifica/senarios_merge_base/FSTMerge/merge.expression --base-directory /workspaces/Pesquisa-cientifica/senarios_merge_base/FSTMerge)
----------------------------------------------------------------------------------------------

Para rodar o IntelliMerge, temos que apenas executar o arquivo.jar:

para rodar IntelliMerge: java -jar ./IntelliMerge/IntelliMerge-1.0.9-all.jar -d "/workspaces/Pesquisa-cientifica/senarios_merge_base/IntelliMerge/scenario_12/left" "/workspaces/Pesquisa-cientifica/senarios_merge_base/IntelliMerge/scenario_12/base" "/workspaces/Pesquisa-cientifica/senarios_merge_base/IntelliMerge/scenario_12/right" -o "/workspaces/Pesquisa-cientifica/output/IntelliMerge/scenario_12"
---------------------------------------------------------------------------------------------

Para rodar o AutoMerge, temos que fazer o download da versão pelo menos do Java 8 até 11 e executar o java junto com a execução da ferramenta.

./java-versions/jdk-11.0.2/bin/java -cp ./AutoMerge/AutoMerge.jar:libs/activation-1.1.1.jar \de.fosd.jdime.Main \-m structured \-f \-o /workspaces/Pesquisa-cientifica/output/AutoMerge/scenario_1.java \/workspaces/Pesquisa-cientifica/senarios_merge_base/AutoMerge/scenario_1/base/Person.java \/workspaces/Pesquisa-cientifica/senarios_merge_base/AutoMerge/scenario_1/left/Person.java \/workspaces/Pesquisa-cientifica/senarios_merge_base/AutoMerge/scenario_1/right/Person.java

para executar o AutoMerge com o structured: ./java-versions/jdk-11.0.2/bin/java -cp ./AutoMerge/AutoMerge.jar:libs/activation-1.1.1.jar \de.fosd.jdime.Main \-m structured \-f \-o /workspaces/Pesquisa-cientifica/output/AutoMerge/output.java \/workspaces/Pesquisa-cientifica/senarios_merge_base/AutoMerge/base/SimpleClass.java \/workspaces/Pesquisa-cientifica/senarios_merge_base/AutoMerge/left/SimpleClass.java \/workspaces/Pesquisa-cientifica/senarios_merge_base/AutoMerge/right/SimpleClass.java

para executar o AutoMerge com o linebase: java -Djava.library.path=/usr/lib/x86_64-linux-gnu/ \-cp ./AutoMerge/AutoMerge.jar:libs/activation-1.1.1.jar \de.fosd.jdime.Main \-m linebased \-f \-o /workspaces/Pesquisa-cientifica/output/AutoMerge/output.java \/workspaces/Pesquisa-cientifica/senarios_merge_base/AutoMerge/base/SimpleClass.java \/workspaces/Pesquisa-cientifica/senarios_merge_base/AutoMerge/left/SimpleClass.java \/workspaces/Pesquisa-cientifica/senarios_merge_base/AutoMerge/right/SimpleClass.java
---------------------------------------------------------------------------------------------------------------

para rodar o kdiff3 em ambientes com GUI:kdiff3 \
/workspaces/Pesquisa-cientifica/senarios_merge_base/KDiff3/base/SimpleClass.java \
/workspaces/Pesquisa-cientifica/senarios_merge_base/KDiff3/left/SimpleClass.java \
/workspaces/Pesquisa-cientifica/senarios_merge_base/KDiff3/right/SimpleClass.java \
-m --batch -o /workspaces/Pesquisa-cientifica/output/KDiff3/output.java

----------------------------------------------------------------------------------------------------------

para rodar o JDime: JAVA_HOME=/workspaces/Pesquisa-cientifica/java-versions/jdk8u392-b08 ./JDime/jdime/build/install/JDime/bin/JDime --mode structured --output ./output/JDime/scenario_12 ./senarios_merge_base/JDime/scenario_12/left ./senarios_merge_base/JDime/scenario_12/base ./senarios_merge_base/JDime/scenario_12/right