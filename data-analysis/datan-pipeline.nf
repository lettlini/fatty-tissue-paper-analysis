workflow {
    new File(params.parent_outdir).deleteDir()
    new File(params.parent_outdir).mkdirs()

    python_files_ch = Channel.fromPath("${projectDir}/analysis-scripts/**/*.py", hidden: false)

    execute_python(python_files_ch, params.data_preparation_dir, params.parent_outdir)
}

process execute_python {

    publishDir "${parent_dir_out}/${python_file.baseName}", mode: 'copy'

    input:
    path python_file
    path data_preparation_dir
    val parent_dir_out

    output:
    path "*"

    script:
    """
    python ${python_file} \
        --data_preparation_dir=${data_preparation_dir} \
        --parent_dir_out="." \
        --cell_class="HeLa_CaSki"
    """
}
