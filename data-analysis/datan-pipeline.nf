workflow {
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
    path "results_folder/*"

    script:
    """
        mkdir -p results_folder/
        python ${python_file} \
            --data_preparation_dir=${data_preparation_dir} \
            --parent_dir_out="results_folder" \
            --cell_class="HeLa_CaSki"
    """
}
