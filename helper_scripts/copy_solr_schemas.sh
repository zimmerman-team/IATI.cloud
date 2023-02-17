clear
cores=("activity" "budget" "dataset"  "organisation" "publisher" "result" "transaction")
basedir=""

# request the users input for the directory
select yn in "/var/solr/data" "/opt/solr/server/solr" "/home/zimmerman/Installs/solr-8.11.2/server/solr" "Other... which is:"; do
    case $yn in
        "/home/zimmerman/Installs/solr-8.11.2/server/solr" ) basedir=/home/zimmerman/Installs/solr-8.11.2/server/solr; break;;
        "/opt/solr/server/solr" ) basedir=/opt/solr/server/solr; break;;
        "/var/solr/data" ) basedir=/var/solr/data; break;;
        "Other... which is:" ) read basedir; break;;
    esac
done

replaceall () {
    for i in "${cores[@]}"
    do
    : 
        cp ../OIPA/direct_indexing/solr/cores/$i/managed-schema $basedir/$i/conf
    done
}

replaceeach () {
    for i in "${cores[@]}"
    do
    : 
        echo ""
        read -p "Do you wish to update core $i? " yn
        case $yn in
            [Yy]* ) echo "Updating $i"; cp ../OIPA/direct_indexing/solr/cores/$i/managed-schema $basedir/$i/conf;;
            * ) echo "Skipping $i";;
        esac
    done
    
}

echo "Should I replace all cores? (y/n)"
select yn in "Replace all cores" "Replace specific cores"; do
    case $yn in
        "Replace all cores" ) replaceall; break;;
        "Replace specific cores" ) replaceeach; break;;
    esac
done

echo "Done..."
