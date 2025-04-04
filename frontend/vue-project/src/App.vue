<script setup>
import { ref, onMounted } from 'vue';

// Estado reativo para armazenar os dados das operadoras
const operadoras = ref([]);
// Estado para controle de carregamento
const isLoading = ref(true);
// Estado para mensagens de erro
const error = ref(null);
// Termo de busca
const searchTerm = ref('');
// Dados filtrados
const filteredOperadoras = ref([]);
// Colunas a serem exibidas na tabela (Ajuste conforme as colunas REAIS do seu CSV)
const colunasVisiveis = ref([
  'Registro ANS',
  'CNPJ',
  'Razão Social',
  'Nome Fantasia',
  'Modalidade',
  'Logradouro',
  'Número',
  'Complemento',
  'Bairro',
  'Cidade',
  'UF',
  'CEP',
  'DDD',
  'Telefone',
  'Fax',
  'Endereço eletrônico',
  'Representante',
  'Cargo Representante',
  'Data Registro ANS'
]); // <= IMPORTANTE: Verifique e ajuste esses nomes com os do seu CSV!

// Função para buscar os dados da API backend
async function fetchOperadoras() {
  isLoading.value = true;
  error.value = null;
  operadoras.value = []; // Limpa dados antigos
  filteredOperadoras.value = [];

  try {
    // A URL da sua API Flask (verifique a porta se não for 5000)
    const response = await fetch('http://localhost:5000/api/operadoras');

    if (!response.ok) {
      // Se a resposta não for OK (e.g., 404, 500), lança um erro
      const errorData = await response.json().catch(() => ({ message: response.statusText }));
      throw new Error(`Erro ${response.status}: ${errorData.message || response.statusText}`);
    }

    const data = await response.json();
    operadoras.value = data;
    filterData(); // Aplica o filtro inicial (mostra tudo)
    console.log(`Recebidos ${data.length} registros da API.`);

  } catch (err) {
    console.error('Falha ao buscar dados da API:', err);
    error.value = `Não foi possível carregar os dados. ${err.message}. Verifique se o backend está rodando e acessível.`;
  } finally {
    // Marca que o carregamento terminou (com sucesso ou erro)
    isLoading.value = false;
  }
}

// Função para filtrar os dados com base no searchTerm
function filterData() {
  if (!searchTerm.value) {
    filteredOperadoras.value = operadoras.value; // Mostra tudo se a busca estiver vazia
  } else {
    const lowerCaseSearchTerm = searchTerm.value.toLowerCase();
    filteredOperadoras.value = operadoras.value.filter(op => {
      // Verifica se algum valor em alguma coluna visível contém o termo de busca
      return colunasVisiveis.value.some(coluna =>
        op[coluna] && op[coluna].toString().toLowerCase().includes(lowerCaseSearchTerm)
      );
    });
  }
}

// Hook do ciclo de vida: chama fetchOperadoras quando o componente é montado
onMounted(() => {
  fetchOperadoras();
});
</script>

<template>
  <div id="app">
    <h1>Operadoras de Planos de Saúde Ativas na ANS</h1>

    <!-- Mensagem de Erro -->
    <div v-if="error" class="error-message">
      <p><strong>Erro:</strong> {{ error }}</p>
      <button @click="fetchOperadoras">Tentar Novamente</button>
    </div>

    <!-- Mensagem de Carregamento -->
    <div v-if="isLoading" class="loading-message">
      <p>Carregando dados das operadoras...</p>
    </div>

    <!-- Conteúdo Principal (após carregar e sem erros) -->
    <div v-if="!isLoading && !error">
       <!-- Campo de Busca -->
       <div class="search-container">
         <label for="search">Buscar:</label>
         <input
           type="text"
           id="search"
           v-model="searchTerm"
           @input="filterData"
           placeholder="Digite para buscar em qualquer coluna..."
         />
         <span>({{ filteredOperadoras.length }} de {{ operadoras.length }} registros encontrados)</span>
       </div>


      <!-- Tabela de Dados -->
      <div class="table-container">
        <table>
          <thead>
            <tr>
              <!-- Gera os cabeçalhos da tabela dinamicamente -->
              <th v-for="coluna in colunasVisiveis" :key="coluna">{{ coluna }}</th>
            </tr>
          </thead>
          <tbody>
            <!-- Itera sobre os dados FILTRADOS -->
            <tr v-for="(operadora, index) in filteredOperadoras" :key="operadora['Registro ANS'] || index">
              <!-- Gera as células da linha dinamicamente -->
              <td v-for="coluna in colunasVisiveis" :key="coluna">
                {{ operadora[coluna] }}
              </td>
            </tr>
            <!-- Mensagem se a busca não retornar resultados -->
             <tr v-if="filteredOperadoras.length === 0 && operadoras.length > 0">
                <td :colspan="colunasVisiveis.length" class="no-results">
                  Nenhum registro encontrado para "{{ searchTerm }}".
                </td>
              </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<style scoped>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  color: #2c3e50;
  margin: 20px;
  max-width: 95%; /* Ajuste conforme necessário */
  margin-left: auto;
  margin-right: auto;
}

h1 {
  text-align: center;
  color: #42b983;
}

.loading-message, .error-message {
  text-align: center;
  padding: 20px;
  font-size: 1.2em;
}

.error-message {
  color: #d8000c;
  background-color: #ffd2d2;
  border: 1px solid #d8000c;
  border-radius: 5px;
}

.error-message button {
    margin-left: 15px;
    padding: 5px 10px;
    cursor: pointer;
}

.search-container {
    margin-bottom: 15px;
    padding: 10px;
    background-color: #f8f8f8;
    border-radius: 5px;
}

.search-container label {
    margin-right: 10px;
    font-weight: bold;
}

.search-container input {
    padding: 8px;
    border: 1px solid #ccc;
    border-radius: 4px;
    width: 300px; /* Ajuste a largura conforme necessário */
    margin-right: 10px;
}

 .search-container span {
    font-size: 0.9em;
    color: #555;
}

.table-container {
  max-height: 70vh; /* Altura máxima antes de mostrar barra de rolagem */
  overflow: auto;   /* Adiciona barras de rolagem se necessário */
  border: 1px solid #ddd;
}

table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.9em;
}

th, td {
  border: 1px solid #ddd;
  padding: 8px;
  text-align: left;
  /* Evita quebra de linha excessiva */
  white-space: nowrap;
  /* Adiciona '...' se o conteúdo for muito longo */
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 200px; /* Largura máxima da coluna, ajuste se necessário */
}

th {
  background-color: #42b983;
  color: white;
  position: sticky; /* Faz o cabeçalho ficar fixo ao rolar */
  top: 0;           /* Necessário para sticky funcionar */
  z-index: 1;       /* Garante que o cabeçalho fique sobre o conteúdo */
}

tbody tr:nth-child(even) {
  background-color: #f9f9f9;
}

tbody tr:hover {
  background-color: #f1f1f1;
}

 .no-results td {
    text-align: center;
    font-style: italic;
    color: #777;
    padding: 20px;
 }
</style>