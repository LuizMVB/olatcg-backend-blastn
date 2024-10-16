set -ex

echo "Updating package lists"
apt-get update
echo "Installing dependencies"
apt-get install -y wget libgomp1 ncbi-blast+ fasttree muscle curl

echo "Creating directories"
mkdir -p /blast/taxonomy /blast/sequences /blast/db

echo "Downloading sequences"

# Bactérias de ambientes sadios (solo e água)
wget -O /blast/sequences/Acinetobacter_johnsonii_genomic.fna.gz https://ftp.ncbi.nlm.nih.gov/genomes/refseq/bacteria/Acinetobacter_johnsonii/latest_assembly_versions/GCF_000162055.1_ASM16205v1/GCF_000162055.1_ASM16205v1_genomic.fna.gz
wget -O /blast/sequences/Acinetobacter_johnsonii_genomic.gbff.gz https://ftp.ncbi.nlm.nih.gov/genomes/refseq/bacteria/Acinetobacter_johnsonii/latest_assembly_versions/GCF_000162055.1_ASM16205v1/GCF_000162055.1_ASM16205v1_genomic.gbff.gz

wget -O /blast/sequences/Bacillus_cereus_genomic.fna.gz https://ftp.ncbi.nlm.nih.gov/genomes/refseq/bacteria/Bacillus_cereus_group_sp._BY10-2LC/latest_assembly_versions/GCF_027711705.1_ASM2771170v1/GCF_027711705.1_ASM2771170v1_genomic.fna.gz
wget -O /blast/sequences/Bacillus_cereus_genomic.gbff.gz https://ftp.ncbi.nlm.nih.gov/genomes/refseq/bacteria/Bacillus_cereus_group_sp._BY10-2LC/latest_assembly_versions/GCF_027711705.1_ASM2771170v1/GCF_027711705.1_ASM2771170v1_genomic.gbff.gz

wget -O /blast/sequences/Bacillus_sphaericus_genomic.fna.gz https://ftp.ncbi.nlm.nih.gov/genomes/refseq/bacteria/Lysinibacillus_sphaericus/latest_assembly_versions/GCF_000017965.1_ASM1796v1/GCF_000017965.1_ASM1796v1_genomic.fna.gz
wget -O /blast/sequences/Bacillus_sphaericus_genomic.gbff.gz https://ftp.ncbi.nlm.nih.gov/genomes/refseq/bacteria/Lysinibacillus_sphaericus/latest_assembly_versions/GCF_000017965.1_ASM1796v1/GCF_000017965.1_ASM1796v1_genomic.gbff.gz

wget -O /blast/sequences/Bacillus_thuringiensis_genomic.fna.gz https://ftp.ncbi.nlm.nih.gov/genomes/refseq/bacteria/Bacillus_thuringiensis/latest_assembly_versions/GCF_000008505.1_ASM850v1/GCF_000008505.1_ASM850v1_genomic.fna.gz
wget -O /blast/sequences/Bacillus_thuringiensis_genomic.gbff.gz https://ftp.ncbi.nlm.nih.gov/genomes/refseq/bacteria/Bacillus_thuringiensis/latest_assembly_versions/GCF_000008505.1_ASM850v1/GCF_000008505.1_ASM850v1_genomic.gbff.gz

wget -O /blast/sequences/Burkholderia_cepacia_genomic.fna.gz https://ftp.ncbi.nlm.nih.gov/genomes/refseq/bacteria/Burkholderia_cepacia/latest_assembly_versions/GCF_000292915.1_ASM29291v1/GCF_000292915.1_ASM29291v1_genomic.fna.gz
wget -O /blast/sequences/Burkholderia_cepacia_genomic.gbff.gz https://ftp.ncbi.nlm.nih.gov/genomes/refseq/bacteria/Burkholderia_cepacia/latest_assembly_versions/GCF_000292915.1_ASM29291v1/GCF_000292915.1_ASM29291v1_genomic.gbff.gz

# Bactérias do ciclo do nitrogênio
wget -O /blast/sequences/Nitrobacter_sp_genomic.fna.gz https://ftp.ncbi.nlm.nih.gov/genomes/refseq/bacteria/Nitrobacter_sp./latest_assembly_versions/GCF_017306235.1_ASM1730623v1/GCF_017306235.1_ASM1730623v1_genomic.fna.gz
wget -O /blast/sequences/Nitrobacter_sp_genomic.gbff.gz https://ftp.ncbi.nlm.nih.gov/genomes/refseq/bacteria/Nitrobacter_sp./latest_assembly_versions/GCF_017306235.1_ASM1730623v1/GCF_017306235.1_ASM1730623v1_genomic.gbff.gz

wget -O /blast/sequences/Nitrobacter_winogradskyi_genomic.fna.gz https://ftp.ncbi.nlm.nih.gov/genomes/refseq/bacteria/Nitrobacter_winogradskyi/latest_assembly_versions/GCF_000012725.1_ASM1272v1/GCF_000012725.1_ASM1272v1_genomic.fna.gz
wget -O /blast/sequences/Nitrobacter_winogradskyi_genomic.gbff.gz https://ftp.ncbi.nlm.nih.gov/genomes/refseq/bacteria/Nitrobacter_winogradskyi/latest_assembly_versions/GCF_000012725.1_ASM1272v1/GCF_000012725.1_ASM1272v1_genomic.gbff.gz

wget -O /blast/sequences/Nitrosomonas_sp_genomic.fna.gz https://ftp.ncbi.nlm.nih.gov/genomes/refseq/bacteria/Nitrosomonas_sp./latest_assembly_versions/GCF_003501205.1_ASM350120v1/GCF_003501205.1_ASM350120v1_genomic.fna.gz
wget -O /blast/sequences/Nitrosomonas_sp_genomic.gbff.gz https://ftp.ncbi.nlm.nih.gov/genomes/refseq/bacteria/Nitrosomonas_sp./latest_assembly_versions/GCF_003501205.1_ASM350120v1/GCF_003501205.1_ASM350120v1_genomic.gbff.gz

wget -O /blast/sequences/Nitrosomonas_europaea_genomic.fna.gz https://ftp.ncbi.nlm.nih.gov/genomes/refseq/bacteria/Nitrosomonas_europaea/latest_assembly_versions/GCF_000009145.1_ASM914v1/GCF_000009145.1_ASM914v1_genomic.fna.gz
wget -O /blast/sequences/Nitrosomonas_europaea_genomic.gbff.gz https://ftp.ncbi.nlm.nih.gov/genomes/refseq/bacteria/Nitrosomonas_europaea/latest_assembly_versions/GCF_000009145.1_ASM914v1/GCF_000009145.1_ASM914v1_genomic.gbff.gz

wget -O /blast/sequences/Rhizobium_leguminosarum_genomic.fna.gz https://ftp.ncbi.nlm.nih.gov/genomes/refseq/bacteria/Rhizobium_leguminosarum/latest_assembly_versions/GCF_000021345.1_ASM2134v1/GCF_000021345.1_ASM2134v1_genomic.fna.gz
wget -O /blast/sequences/Rhizobium_leguminosarum_genomic.gbff.gz https://ftp.ncbi.nlm.nih.gov/genomes/refseq/bacteria/Rhizobium_leguminosarum/latest_assembly_versions/GCF_000021345.1_ASM2134v1/GCF_000021345.1_ASM2134v1_genomic.gbff.gz

wget -O /blast/sequences/Rhizobium_etli_genomic.fna.gz https://ftp.ncbi.nlm.nih.gov/genomes/refseq/bacteria/Rhizobium_etli/latest_assembly_versions/GCF_000092045.1_ASM9204v1/GCF_000092045.1_ASM9204v1_genomic.fna.gz
wget -O /blast/sequences/Rhizobium_etli_genomic.gbff.gz https://ftp.ncbi.nlm.nih.gov/genomes/refseq/bacteria/Rhizobium_etli/latest_assembly_versions/GCF_000092045.1_ASM9204v1/GCF_000092045.1_ASM9204v1_genomic.gbff.gz

# Cianobactérias
wget -O /blast/sequences/Gloeobacter_violaceus_genomic.fna.gz https://ftp.ncbi.nlm.nih.gov/genomes/refseq/bacteria/Gloeobacter_violaceus/latest_assembly_versions/GCF_000011385.1_ASM1138v1/GCF_000011385.1_ASM1138v1_genomic.fna.gz
wget -O /blast/sequences/Gloeobacter_violaceus_genomic.gbff.gz https://ftp.ncbi.nlm.nih.gov/genomes/refseq/bacteria/Gloeobacter_violaceus/latest_assembly_versions/GCF_000011385.1_ASM1138v1/GCF_000011385.1_ASM1138v1_genomic.gbff.gz

wget -O /blast/sequences/G_kilaueensis_genomic.fna.gz https://ftp.ncbi.nlm.nih.gov/genomes/refseq/bacteria/Gloeobacter_kilaueensis/latest_assembly_versions/GCF_000484535.1_ASM48453v1/GCF_000484535.1_ASM48453v1_genomic.fna.gz
wget -O /blast/sequences/G_kilaueensis_genomic.gbff.gz https://ftp.ncbi.nlm.nih.gov/genomes/refseq/bacteria/Gloeobacter_kilaueensis/latest_assembly_versions/GCF_000484535.1_ASM48453v1/GCF_000484535.1_ASM48453v1_genomic.gbff.gz

# Bactérias presentes em esgoto / Coliformes fecais
wget -O /blast/sequences/Escherichia_coli_genomic.fna.gz https://ftp.ncbi.nlm.nih.gov/genomes/all/GCF/000/005/845/GCF_000005845.2_ASM584v2/GCF_000005845.2_ASM584v2_genomic.fna.gz
wget -O /blast/sequences/Escherichia_coli_genomic.gbff.gz https://ftp.ncbi.nlm.nih.gov/genomes/all/GCF/000/005/845/GCF_000005845.2_ASM584v2/GCF_000005845.2_ASM584v2_genomic.gbff.gz

wget -O /blast/sequences/Enterobacter_cloacae_genomic.fna.gz https://ftp.ncbi.nlm.nih.gov/genomes/all/GCF/905/331/265/GCF_905331265.2_AI2999v1_cpp/GCF_905331265.2_AI2999v1_cpp_genomic.fna.gz
wget -O /blast/sequences/Enterobacter_cloacae_genomic.gbff.gz https://ftp.ncbi.nlm.nih.gov/genomes/all/GCF/905/331/265/GCF_905331265.2_AI2999v1_cpp/GCF_905331265.2_AI2999v1_cpp_genomic.gbff.gz

wget -O /blast/sequences/Klebsiella_pneumoniae_genomic.fna.gz https://ftp.ncbi.nlm.nih.gov/genomes/all/GCF/000/240/185/GCF_000240185.1_ASM24018v2/GCF_000240185.1_ASM24018v2_genomic.fna.gz
wget -O /blast/sequences/Klebsiella_pneumoniae_genomic.gbff.gz https://ftp.ncbi.nlm.nih.gov/genomes/all/GCF/000/240/185/GCF_000240185.1_ASM24018v2/GCF_000240185.1_ASM24018v2_genomic.gbff.gz

# Bactérias de ambientes hospitalar
wget -O /blast/sequences/Pseudomonas_aeruginosa.fna.gz https://ftp.ncbi.nlm.nih.gov/genomes/all/GCF/000/006/765/GCF_000006765.1_ASM676v1/GCF_000006765.1_ASM676v1_genomic.fna.gz
wget -O /blast/sequences/Pseudomonas_aeruginosa.gbff.gz https://ftp.ncbi.nlm.nih.gov/genomes/all/GCF/000/006/765/GCF_000006765.1_ASM676v1/GCF_000006765.1_ASM676v1_genomic.gbff.gz

wget -O /blast/sequences/Serratia_marcescens.fna.gz https://ftp.ncbi.nlm.nih.gov/genomes/all/GCF/030/291/735/GCF_030291735.1_ASM3029173v1/GCF_030291735.1_ASM3029173v1_genomic.fna.gz
wget -O /blast/sequences/Serratia_marcescens.gbff.gz https://ftp.ncbi.nlm.nih.gov/genomes/all/GCF/030/291/735/GCF_030291735.1_ASM3029173v1/GCF_030291735.1_ASM3029173v1_genomic.gbff.gz

wget -O /blast/sequences/Staphylococcus_aureus.fna.gz https://ftp.ncbi.nlm.nih.gov/genomes/all/GCF/000/013/425/GCF_000013425.1_ASM1342v1/GCF_000013425.1_ASM1342v1_genomic.fna.gz
wget -O /blast/sequences/Staphylococcus_aureus.gbff.gz https://ftp.ncbi.nlm.nih.gov/genomes/all/GCF/000/013/425/GCF_000013425.1_ASM1342v1/GCF_000013425.1_ASM1342v1_genomic.gbff.gz

# Bactérias degradadoras de combustíveis e biocombustíveis
wget -O /blast/sequences/Bacillus_amyloliquefaciens.fna.gz https://ftp.ncbi.nlm.nih.gov/genomes/all/GCF/019/396/925/GCF_019396925.1_ASM1939692v1/GCF_019396925.1_ASM1939692v1_genomic.fna.gz
wget -O /blast/sequences/Bacillus_amyloliquefaciens.gbff.gz https://ftp.ncbi.nlm.nih.gov/genomes/all/GCF/019/396/925/GCF_019396925.1_ASM1939692v1/GCF_019396925.1_ASM1939692v1_genomic.gbff.gz

wget -O /blast/sequences/Arthrobacter_sp.fna.gz https://ftp.ncbi.nlm.nih.gov/genomes/all/GCA/031/277/795/GCA_031277795.1_ASM3127779v1/GCA_031277795.1_ASM3127779v1_genomic.fna.gz
wget -O /blast/sequences/Arthrobacter_sp.gbff.gz https://ftp.ncbi.nlm.nih.gov/genomes/all/GCA/031/277/795/GCA_031277795.1_ASM3127779v1/GCA_031277795.1_ASM3127779v1_genomic.gbff.gz

wget -O /blast/sequences/Lysobacter_sp.fna.gz https://ftp.ncbi.nlm.nih.gov/genomes/all/GCA/013/141/175/GCA_013141175.1_ASM1314117v1/GCA_013141175.1_ASM1314117v1_genomic.fna.gz
wget -O /blast/sequences/Lysobacter_sp.gbff.gz https://ftp.ncbi.nlm.nih.gov/genomes/all/GCA/013/141/175/GCA_013141175.1_ASM1314117v1/GCA_013141175.1_ASM1314117v1_genomic.gbff.gz

wget -O /blast/sequences/Burkholderia_sp.fna.gz https://ftp.ncbi.nlm.nih.gov/genomes/all/GCA/040/954/445/GCA_040954445.1_ASM4095444v1/GCA_040954445.1_ASM4095444v1_genomic.fna.gz
wget -O /blast/sequences/Burkholderia_sp.gbff.gz https://ftp.ncbi.nlm.nih.gov/genomes/all/GCA/040/954/445/GCA_040954445.1_ASM4095444v1/GCA_040954445.1_ASM4095444v1_genomic.gbff.gz

wget -O /blast/sequences/Burkholderia_cepacia.fna.gz https://ftp.ncbi.nlm.nih.gov/genomes/all/GCF/009/586/235/GCF_009586235.1_ASM958623v1/GCF_009586235.1_ASM958623v1_genomic.fna.gz
wget -O /blast/sequences/Burkholderia_cepacia.gbff.gz https://ftp.ncbi.nlm.nih.gov/genomes/all/GCF/009/586/235/GCF_009586235.1_ASM958623v1/GCF_009586235.1_ASM958623v1_genomic.gbff.gz

wget -O /blast/sequences/Exiguobacterium_aurantiacum.fna.gz https://ftp.ncbi.nlm.nih.gov/genomes/all/GCF/000/702/585/GCF_000702585.1_ASM70258v1/GCF_000702585.1_ASM70258v1_genomic.fna.gz
wget -O /blast/sequences/Exiguobacterium_aurantiacum.gbff.gz https://ftp.ncbi.nlm.nih.gov/genomes/all/GCF/000/702/585/GCF_000702585.1_ASM70258v1/GCF_000702585.1_ASM70258v1_genomic.gbff.gz

# Bactérias degradadoras de pesticidas
wget -O /blast/sequences/Burkholderia_cepacia.fna.gz https://ftp.ncbi.nlm.nih.gov/genomes/all/GCF/009/586/235/GCF_009586235.1_ASM958623v1/GCF_009586235.1_ASM958623v1_genomic.fna.gz
wget -O /blast/sequences/Burkholderia_cepacia.gbff.gz https://ftp.ncbi.nlm.nih.gov/genomes/all/GCF/009/586/235/GCF_009586235.1_ASM958623v1/GCF_009586235.1_ASM958623v1_genomic.gbff.gz

wget -O /blast/sequences/Pseudomonas_aeruginosa.fna.gz https://ftp.ncbi.nlm.nih.gov/genomes/all/GCF/000/006/765/GCF_000006765.1_ASM676v1/GCF_000006765.1_ASM676v1_genomic.fna.gz
wget -O /blast/sequences/Pseudomonas_aeruginosa.gbff.gz https://ftp.ncbi.nlm.nih.gov/genomes/all/GCF/000/006/765/GCF_000006765.1_ASM676v1/GCF_000006765.1_ASM676v1_genomic.gbff.gz

wget -O /blast/sequences/Alcaligenes_eutrophus.fna.gz https://ftp.ncbi.nlm.nih.gov/genomes/all/GCF/000/219/215/GCF_000219215.1_ASM21921v1/GCF_000219215.1_ASM21921v1_genomic.fna.gz
wget -O /blast/sequences/Alcaligenes_eutrophus.gbff.gz https://ftp.ncbi.nlm.nih.gov/genomes/all/GCF/000/219/215/GCF_000219215.1_ASM21921v1/GCF_000219215.1_ASM21921v1_genomic.gbff.gz

# Bactérias degradadoras de metais (pesados)
wget -O /blast/sequences/Cupriavidus_metallidurans.fna.gz https://ftp.ncbi.nlm.nih.gov/genomes/all/GCF/900/185/755/GCF_900185755.1_NDB4MOL1_Assembly_1/GCF_900185755.1_NDB4MOL1_Assembly_1_genomic.fna.gz
wget -O /blast/sequences/Cupriavidus_metallidurans.gbff.gz https://ftp.ncbi.nlm.nih.gov/genomes/all/GCF/900/185/755/GCF_900185755.1_NDB4MOL1_Assembly_1/GCF_900185755.1_NDB4MOL1_Assembly_1_genomic.gbff.gz

wget -O /blast/sequences/Pseudomonas_aeruginosa.fna.gz https://ftp.ncbi.nlm.nih.gov/genomes/all/GCF/000/006/765/GCF_000006765.1_ASM676v1/GCF_000006765.1_ASM676v1_genomic.fna.gz
wget -O /blast/sequences/Pseudomonas_aeruginosa.gbff.gz https://ftp.ncbi.nlm.nih.gov/genomes/all/GCF/000/006/765/GCF_000006765.1_ASM676v1/GCF_000006765.1_ASM676v1_genomic.gbff.gz

wget -O /blast/sequences/Shewanella_oneidensis.fna.gz https://ftp.ncbi.nlm.nih.gov/genomes/all/GCF/000/146/165/GCF_000146165.2_ASM14616v2/GCF_000146165.2_ASM14616v2_genomic.fna.gz
wget -O /blast/sequences/Shewanella_oneidensis.gbff.gz https://ftp.ncbi.nlm.nih.gov/genomes/all/GCF/000/146/165/GCF_000146165.2_ASM14616v2/GCF_000146165.2_ASM14616v2_genomic.gbff.gz

# Bactérias presentes em efluentes industriais
wget -O /blast/sequences/Acinetobacter_baumannii.fna.gz https://ftp.ncbi.nlm.nih.gov/genomes/all/GCF/009/035/845/GCF_009035845.1_ASM903584v1/GCF_009035845.1_ASM903584v1_genomic.fna.gz
wget -O /blast/sequences/Acinetobacter_baumannii.gbff.gz https://ftp.ncbi.nlm.nih.gov/genomes/all/GCF/009/035/845/GCF_009035845.1_ASM903584v1/GCF_009035845.1_ASM903584v1_genomic.gbff.gz

wget -O /blast/sequences/Stenotrophomonas_maltophilia.fna.gz https://ftp.ncbi.nlm.nih.gov/genomes/all/GCF/900/186/865/GCF_900186865.1_49243_F02/GCF_900186865.1_49243_F02_genomic.fna.gz
wget -O /blast/sequences/Stenotrophomonas_maltophilia.gbff.gz https://ftp.ncbi.nlm.nih.gov/genomes/all/GCF/900/186/865/GCF_900186865.1_49243_F02/GCF_900186865.1_49243_F02_genomic.gbff.gz

wget -O /blast/sequences/Thiobacillus.fna.gz https://ftp.ncbi.nlm.nih.gov/genomes/all/GCF/000/376/425/GCF_000376425.1_ASM37642v1/GCF_000376425.1_ASM37642v1_genomic.fna.gz
wget -O /blast/sequences/Thiobacillus.gbff.gz https://ftp.ncbi.nlm.nih.gov/genomes/all/GCF/000/376/425/GCF_000376425.1_ASM37642v1/GCF_000376425.1_ASM37642v1_genomic.gbff.gz

wget -O /blast/sequences/Desulfovibrio_desulfuricans.fna.gz https://ftp.ncbi.nlm.nih.gov/genomes/all/GCF/017/815/575/GCF_017815575.1_ASM1781557v1/GCF_017815575.1_ASM1781557v1_genomic.fna.gz
wget -O /blast/sequences/Desulfovibrio_desulfuricans.gbff.gz https://ftp.ncbi.nlm.nih.gov/genomes/all/GCF/017/815/575/GCF_017815575.1_ASM1781557v1/GCF_017815575.1_ASM1781557v1_genomic.gbff.gz

echo "Downloading taxonomy data"
wget -P /blast/taxonomy https://ftp.ncbi.nlm.nih.gov/pub/taxonomy/taxdump.tar.gz
tar -xvzf /blast/taxonomy/taxdump.tar.gz -C /blast/taxonomy nodes.dmp names.dmp

echo "Downloading BLAST database"
wget -P /blast/db https://ftp.ncbi.nlm.nih.gov/blast/db/taxdb.tar.gz
tar -xvzf /blast/db/taxdb.tar.gz -C /blast/db

echo "Setting up Python environment"
python -m venv /py
/py/bin/pip install --upgrade pip

echo "Installing PostgreSQL client and build essentials"
apt-get install -y postgresql-client
apt-get install -y --no-install-recommends build-essential libpq-dev
/py/bin/pip install -r /requirements.txt

echo "Unzip /sequences/*"
gunzip -f /blast/sequences/*.gz

# Criar o mapa de taxid a partir de todos os arquivos .gbff
echo "Creating taxid map"
find /blast/sequences -name "*.gbff" | while read gbff_file; do
    /py/bin/python3 /build/create_taxid_map.py -i "$gbff_file" -o /blast/taxonomy/taxid_map.txt --append
done

echo "Creating BLAST database"
rm -f /blast/combined_sequences.fna
touch /blast/combined_sequences.fna

# Para cada arquivo .fna no diretório /blast/sequences
for fna_file in /blast/sequences/*.fna; do
  # Captura apenas a primeira sequência (linha de cabeçalho e a sequência)
  awk '/^>/ {if (seq) exit; seq=1} {print}' "$fna_file" >> /blast/combined_sequences.fna
done

# Cria o banco de dados BLAST com o arquivo combinado
makeblastdb -in /blast/combined_sequences.fna -dbtype nucl -parse_seqids -taxid_map /blast/taxonomy/taxid_map.txt -out /blast/db/environmental_bacteria_db

echo "Cleaning up"
apt-get remove -y build-essential libpq-dev wget
rm -rf /var/lib/apt/lists/*
apt-get autoremove -y
apt-get clean
rm -rf /var/lib/apt/lists/*

echo "Setup complete"