"""
in node_modules/prettier-plugin-sh/lib/cjs.js
comment:
           // ".dockerfile"
           // "Dockerfile"
# save 8Mo
rm node_modules/prettier/esm -rf
"""

from node_vm2 import NodeVM

js = """
const prettier = require("prettier");

exports.getFileInfo = (file) => {
   return new Promise(resolve => {
       prettier.resolveConfig(file, {editorconfig: true}).then((config) => {
       prettier.getFileInfo(file, {ignorePath: '.prettierignore'}).then((result) => {
           resolve({
               config: config,
               info: result
            });
        });
        });
    });
};

exports.format = (code, config) => {return prettier.format(code, config)};

exports.check = (code, config) => {return prettier.check(code, config)};

exports.info = () => prettier.getSupportInfo();
"""

with NodeVM.code(
    js,
    "/home/external/workspace/c2cgeoportal/node_modules",
    console="inherit",
    require={
        "external": True,
        #        "internal": True,
    },
) as module:
    #    print(module.call_member("info"))
    a = module.call_member("getFileInfo", "test.js")
    print(a["info"]["ignored"])
    config = a["config"]
    config["parser"] = a["info"]["inferredParser"]
    print(config)

    with open("test.js") as the_file_to_check:
        print(module.call_member("check", the_file_to_check.read(), config))

    with open("test.js") as the_file_to_check:
        new_data = module.call_member("format", the_file_to_check.read(), config)

    with open("test.js", "w") as the_file_to_check:
        the_file_to_check.write(new_data)


test_gql = """
query ($number: Int!) {
  organization(login: "camptocamp") {
    createdAt
    login
    name
    repositories(first: $number) {
      totalCount
      nodes {
        name
        packages(first: $number) {
          nodes {
            name
          }
        }
      }
    }
  }
}
"""
