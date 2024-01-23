param name string
param location string = resourceGroup().location

param principalId string

param databaseName string

param dataActions array = [
  'Microsoft.DocumentDB/databaseAccounts/readMetadata'
  'Microsoft.DocumentDB/databaseAccounts/sqlDatabases/containers/items/*'
  'Microsoft.DocumentDB/databaseAccounts/sqlDatabases/containers/executeQuery'
]

param roleDefinitionName string = 'CosmosDbDataReadWriteRole'

resource cosmosdb 'Microsoft.DocumentDB/databaseAccounts@2021-04-15' = {
  name: name
  location: location
  kind: 'GlobalDocumentDB'
  properties: {
    databaseAccountOfferType: 'Standard'
    locations: [
      {
        locationName: location
        failoverPriority: 0
        isZoneRedundant: false
      }
    ]
    capabilities: [
      {
        name: 'EnableServerless'
      }
    ]
    consistencyPolicy: {
      defaultConsistencyLevel: 'Session'
    }
  }
}

resource sqlDatabase 'Microsoft.DocumentDB/databaseAccounts/sqlDatabases@2021-04-15' = {
  parent: cosmosdb
  name: databaseName
  properties: {
    resource: {
      id: databaseName
    }
    options: {}
  }
}
var roleDefinitionId = guid('sql-role-definition-', principalId, name)
var roleAssignmentId = guid(roleDefinitionId, principalId, name)

resource sqlRoleDefinition 'Microsoft.DocumentDB/databaseAccounts/sqlRoleDefinitions@2021-04-15' = {
  parent: cosmosdb 
  name: roleDefinitionId
  properties: {
    roleName: roleDefinitionName
    type: 'CustomRole'
    assignableScopes: [
      cosmosdb.id
    ]
    permissions: [
      {
        dataActions: dataActions
      }
    ]
  }
}

resource sqlRoleAssignment 'Microsoft.DocumentDB/databaseAccounts/sqlRoleAssignments@2021-04-15' = {
  parent: cosmosdb
  name: roleAssignmentId
  properties: {
    roleDefinitionId: sqlRoleDefinition.id
    principalId: principalId
    scope: cosmosdb.id
  }
}

var containerNames = ['analyses', 'candidates', 'profiles', 'resumes', 'users','uploadruns']

resource sqlContainers 'Microsoft.DocumentDB/databaseAccounts/sqlDatabases/containers@2021-04-15' = [for (containerName, i) in containerNames: {
  parent: sqlDatabase
  name: containerName
  properties: {
    resource: {
      id: containerName
      partitionKey: {
        paths: [
          '/id'
        ]
        kind: 'Hash'
      }
    }
    options: {}
  }
}]

output roleDefinitionId string = sqlRoleDefinition.id
