include { data_preparation } from './data-preparation/pipeline.nf'
include { data_analysis    } from './data-analysis/pipeline.nf'

workflow {
    parent_config = Channel.fromPath(file(params.parent_indir).resolve(params.in_dir).toString() + "/parent.toml", type: "file")
    config_files = Channel.fromPath(file(params.parent_indir).resolve(params.in_dir).toString() + "/**/config.toml", type: "file")

    parent_directories = config_files.flatMap { cfile ->
        def dir = cfile.parent
        def subdirs = dir.listFiles().findAll { it.isDirectory() }
        // assuming the parent directory name is the config type
        subdirs.collect { subdir ->
            [subdir.name, subdir, cfile]
        }
    }

    parent_directories.combine(parent_config)
        | view
}
